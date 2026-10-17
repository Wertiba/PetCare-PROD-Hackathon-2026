"""PDF rendering of a pet report with ReportLab: tables for what to do, charts for how things changed."""

from datetime import UTC, datetime
from io import BytesIO
from pathlib import Path
from xml.sax.saxutils import escape

import anyio
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.legends import Legend
from reportlab.graphics.charts.lineplots import LinePlot
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.widgets.markers import makeMarker
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Image, KeepTogether, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from app.application.ports.pet_report import PetReportRenderer
from app.application.reports.dto import MeasurementSeries, PetReport
from app.domain.categories.enums import CategoryUnit
from app.domain.events.enums import EventPeriod, EventType

_FONTS = Path(__file__).parent / "fonts"
_REGULAR, _BOLD = "Inter", "Inter-SemiBold"

# PROD palette: deep green dominates, mint/cyan/coral are accents.
GREEN = colors.HexColor("#00402E")
MINT = colors.HexColor("#87FAA5")
CYAN = colors.HexColor("#3CDCF5")
CORAL = colors.HexColor("#FF785F")
INK = colors.HexColor("#111111")
MUTED = colors.HexColor("#6B6B6B")
LINE = colors.HexColor("#DADFDC")
TINT = colors.HexColor("#EEF6F1")

_TYPE_LABELS = {
    EventType.VACCINATION: "Прививки",
    EventType.PARASITE_TREATMENT: "Обработки",
    EventType.VET_VISIT: "Ветеринар",
    EventType.MEDICATION: "Лекарства",
    EventType.GROOMING: "Уход",
    EventType.OTHER: "Другое",
}
_TYPE_COLORS = {
    EventType.VACCINATION: GREEN,
    EventType.PARASITE_TREATMENT: CYAN,
    EventType.VET_VISIT: CORAL,
    EventType.MEDICATION: colors.HexColor("#2E8B57"),
    EventType.GROOMING: MINT,
    EventType.OTHER: colors.HexColor("#9AA5A0"),
}
_PERIODS = {
    EventPeriod.NONE: "разово",
    EventPeriod.DAILY: "каждый день",
    EventPeriod.WEEKLY: "раз в неделю",
    EventPeriod.MONTHLY: "раз в месяц",
    EventPeriod.QUARTERLY: "раз в 3 месяца",
    EventPeriod.HALF_YEAR: "раз в полгода",
    EventPeriod.YEARLY: "раз в год",
}
_UNITS = {
    CategoryUnit.G: "г",
    CategoryUnit.ML: "мл",
    CategoryUnit.MIN: "мин",
    CategoryUnit.M: "м",
    CategoryUnit.TIMES: "раз",
    CategoryUnit.RUB: "₽",
    CategoryUnit.POINTS: "баллов",
    CategoryUnit.NONE: "",
}
_MONTHS = ("янв", "фев", "мар", "апр", "май", "июн", "июл", "авг", "сен", "окт", "ноя", "дек")


def _register_fonts() -> None:
    if _REGULAR not in pdfmetrics.getRegisteredFontNames():
        pdfmetrics.registerFont(TTFont(_REGULAR, _FONTS / "Inter-Regular.ttf"))
        pdfmetrics.registerFont(TTFont(_BOLD, _FONTS / "Inter-SemiBold.ttf"))
        pdfmetrics.registerFontFamily(_REGULAR, normal=_REGULAR, bold=_BOLD, italic=_REGULAR, boldItalic=_BOLD)


def _style(name: str, size: float, *, bold: bool = False, color=INK, leading: float | None = None, **extra):
    font = _BOLD if bold else _REGULAR
    return ParagraphStyle(
        name, fontName=font, fontSize=size, leading=leading or size * 1.3, textColor=color, alignment=TA_LEFT, **extra
    )


_TITLE = _style("title", 26, bold=True, color=colors.white, leading=30)
_SUBTITLE = _style("subtitle", 11, color=MINT)
_H2 = _style("h2", 15, bold=True, color=GREEN, spaceBefore=14, spaceAfter=6)
_BODY = _style("body", 9.5)
_SMALL = _style("small", 8.5, color=MUTED)
_CELL = _style("cell", 9)
_CELL_BOLD = _style("cell_bold", 9, bold=True)
_KPI_NUMBER = _style("kpi_number", 22, bold=True, color=GREEN, leading=24)
_KPI_LABEL = _style("kpi_label", 8.5, color=MUTED)
_ALERT = _style("alert", 10, bold=True, color=colors.white)


def _date(moment: float | None) -> str:
    return datetime.fromtimestamp(moment, UTC).strftime("%d.%m.%Y") if moment is not None else "—"


def _plural(number: int, one: str, few: str, many: str) -> str:
    if number % 10 == 1 and number % 100 != 11:
        return one
    if 2 <= number % 10 <= 4 and not 12 <= number % 100 <= 14:
        return few
    return many


def _age(months: int | None) -> str | None:
    if months is None:
        return None
    years, rest = divmod(months, 12)
    parts = []
    if years:
        parts.append(f"{years} {_plural(years, 'год', 'года', 'лет')}")
    if rest or not years:
        parts.append(f"{rest} {_plural(rest, 'месяц', 'месяца', 'месяцев')}")
    return " ".join(parts)


def _days_until(moment: float, now: float) -> str:
    days = int((moment - now) // 86400)
    if moment < now:
        late = max(int((now - moment) // 86400), 0)
        return "просрочено" if late == 0 else f"просрочено на {late} {_plural(late, 'день', 'дня', 'дней')}"
    if days == 0:
        return "сегодня"
    return f"через {days} {_plural(days, 'день', 'дня', 'дней')}"


def _text(value: str) -> str:
    return escape(value).replace("\n", "<br/>")


def _table(rows: list[list], widths: list[float], *, highlight: list[int] | None = None) -> Table:
    table = Table(rows, colWidths=widths, repeatRows=1)
    style = [
        ("FONT", (0, 0), (-1, 0), _BOLD, 8.5),
        ("FONT", (0, 1), (-1, -1), _REGULAR, 9),
        ("TEXTCOLOR", (0, 0), (-1, 0), MUTED),
        ("LINEBELOW", (0, 0), (-1, 0), 0.8, GREEN),
        ("LINEBELOW", (0, 1), (-1, -1), 0.4, LINE),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 3),
    ]
    for row in highlight or []:
        style.append(("BACKGROUND", (0, row), (-1, row), colors.HexColor("#FFE9E4")))
    table.setStyle(TableStyle(style))
    return table


def _header(report: PetReport, width: float) -> Table:
    facts = [part for part in (report.animal, report.breed, _age(report.age_months)) if part]
    lines = [Paragraph(_text(report.pet_name), _TITLE), Spacer(1, 4)]
    if facts:
        lines.append(Paragraph(_text(" · ".join(facts)), _SUBTITLE))
    if report.birth_date is not None:
        lines.append(Paragraph(f"Дата рождения: {_date(report.birth_date)}", _SUBTITLE))
    lines.append(Paragraph(f"Медицинская карта и журнал ухода · {_date(report.generated_at)}", _SUBTITLE))
    photo = _photo(report.photo, 34 * mm)
    table = Table([[lines, photo or ""]], colWidths=[width - 44 * mm, 44 * mm], rowHeights=[46 * mm])
    table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), GREEN),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("ALIGN", (1, 0), (1, 0), "CENTER"),
            ("LEFTPADDING", (0, 0), (0, 0), 8 * mm),
        ])
    )
    return table


def _photo(content: bytes | None, size: float) -> Image | None:
    if not content:
        return None
    try:
        image = Image(BytesIO(content))
    except Exception:  # noqa: BLE001 - a broken photo must not break the whole report
        return None
    scale = size / max(image.imageWidth, image.imageHeight)
    image.drawWidth, image.drawHeight = image.imageWidth * scale, image.imageHeight * scale
    return image


def _kpis(report: PetReport, width: float) -> Table:
    done = report.done_by_type
    tiles = [
        (done.get(EventType.VACCINATION, 0), "прививок сделано"),
        (done.get(EventType.PARASITE_TREATMENT, 0), "обработок от паразитов"),
        (done.get(EventType.VET_VISIT, 0), "визитов к ветеринару"),
        (report.feedings, "записей о питании"),
    ]
    cells = [[Paragraph(str(number), _KPI_NUMBER), Paragraph(label, _KPI_LABEL)] for number, label in tiles]
    gap = 3 * mm
    tile = (width - gap * 3) / 4
    table = Table([cells], colWidths=[tile] * 4, rowHeights=[20 * mm])
    table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), TINT),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 4 * mm),
            ("LINEAFTER", (0, 0), (-2, 0), gap, colors.white),
        ])
    )
    return table


def _alert(report: PetReport, width: float) -> Table | None:
    if not report.overdue:
        return None
    word = _plural(report.overdue, "процедура просрочена", "процедуры просрочены", "процедур просрочено")
    table = Table([[Paragraph(f"⚠ {report.overdue} {word} — запишитесь к врачу или отметьте выполнение", _ALERT)]])
    table._argW = [width]
    table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), CORAL), ("LEFTPADDING", (0, 0), (-1, -1), 4 * mm)]))
    return table


def _upcoming(report: PetReport, width: float) -> list:
    if not report.upcoming:
        return [Paragraph("Запланированных процедур нет.", _SMALL)]
    rows = [["Когда", "Процедура", "Тип", "Срок"]]
    late = []
    for index, event in enumerate(report.upcoming, start=1):
        rows.append([
            _date(event.schedule),
            Paragraph(_text(event.name), _CELL_BOLD if event.is_overdue else _CELL),
            _TYPE_LABELS[event.type],
            _days_until(event.schedule, report.generated_at),
        ])
        if event.is_overdue:
            late.append(index)
    return [_table(rows, [24 * mm, width - 92 * mm, 28 * mm, 40 * mm], highlight=late)]


def _procedures(report: PetReport, width: float) -> list:
    if not report.procedures:
        return [Paragraph("Регулярных процедур пока нет.", _SMALL)]
    rows = [["Процедура", "Как часто", "Сделано", "Последняя", "Следующая"]]
    late = []
    for index, item in enumerate(report.procedures, start=1):
        rows.append([
            Paragraph(_text(item.name), _CELL),
            _PERIODS[item.period],
            str(item.times_done),
            _date(item.last_done),
            _date(item.next_planned),
        ])
        if item.is_overdue:
            late.append(index)
    return [_table(rows, [width - 104 * mm, 30 * mm, 18 * mm, 28 * mm, 28 * mm], highlight=late)]


def _activity_chart(report: PetReport, width: float) -> Drawing | None:
    types = [type_ for type_ in _TYPE_LABELS if any(month.done.get(type_) for month in report.activity)]
    if not types:
        return None
    height = 62 * mm
    drawing = Drawing(width, height)
    chart = VerticalBarChart()
    chart.x, chart.y, chart.width, chart.height = 10 * mm, 12 * mm, width - 52 * mm, height - 16 * mm
    chart.data = [[month.done.get(type_, 0) for month in report.activity] for type_ in types]
    chart.categoryAxis.style = "stacked"
    chart.categoryAxis.categoryNames = [
        _MONTHS[datetime.fromtimestamp(month.month_start, UTC).month - 1] for month in report.activity
    ]
    chart.categoryAxis.labels.fontName = _REGULAR
    chart.categoryAxis.labels.fontSize = 7.5
    chart.categoryAxis.strokeColor = LINE
    chart.valueAxis.valueMin = 0
    chart.valueAxis.labels.fontName = _REGULAR
    chart.valueAxis.labels.fontSize = 7.5
    chart.valueAxis.strokeColor = colors.white
    chart.valueAxis.gridStrokeColor = LINE
    chart.valueAxis.visibleGrid = True
    top = max(sum(column) for column in zip(*chart.data, strict=True))
    chart.valueAxis.valueStep = max(1, round(top / 4))
    chart.barSpacing = 0
    chart.groupSpacing = 6
    for index, type_ in enumerate(types):
        chart.bars[index].fillColor = _TYPE_COLORS[type_]
        chart.bars[index].strokeColor = None
    drawing.add(chart)
    legend = [(_TYPE_COLORS[type_], _TYPE_LABELS[type_]) for type_ in types]
    drawing.add(_legend(legend, width - 38 * mm, height - 6 * mm))
    return drawing


def _legend(items: list, x: float, y: float) -> Legend:
    legend = Legend()
    legend.x, legend.y = x, y
    legend.alignment = "right"
    legend.fontName = _REGULAR
    legend.fontSize = 8
    legend.boxAnchor = "nw"
    legend.columnMaximum = 8
    legend.dx = legend.dy = 7
    legend.deltay = 12
    legend.strokeColor = None
    legend.colorNamePairs = items
    return legend


def _scaled(series: MeasurementSeries) -> tuple[list[tuple[float, float]], str]:
    """Grams above a kilo read better as kilograms, millilitres as litres."""
    values = [value for _, value in series.points]
    if series.unit == CategoryUnit.G and max(values) >= 1000:
        return [(moment, value / 1000) for moment, value in series.points], "кг"
    if series.unit == CategoryUnit.ML and max(values) >= 1000:
        return [(moment, value / 1000) for moment, value in series.points], "л"
    return [(moment, float(value)) for moment, value in series.points], _UNITS[series.unit]


def _number(value: float) -> str:
    return f"{value:.1f}".rstrip("0").rstrip(".").replace(".", ",")


def _series_chart(series: MeasurementSeries, width: float) -> list:
    points, unit = _scaled(series)
    first, last = points[0][1], points[-1][1]
    change = last - first
    sign = "+" if change > 0 else "−" if change < 0 else "±"
    caption = (
        f"<b>{_text(series.name)}</b>{', ' + unit if unit else ''} · {_date(points[0][0])}: {_number(first)} → "
        f"{_date(points[-1][0])}: {_number(last)} ({sign}{_number(abs(change))})"
    )
    height = 50 * mm
    drawing = Drawing(width, height)
    plot = LinePlot()
    plot.x, plot.y, plot.width, plot.height = 14 * mm, 9 * mm, width - 20 * mm, height - 13 * mm
    plot.data = [points]
    plot.lines[0].strokeColor = GREEN
    plot.lines[0].strokeWidth = 2
    plot.lines[0].symbol = makeMarker("FilledCircle", size=3.5, fillColor=MINT, strokeColor=GREEN)
    low, high = min(value for _, value in points), max(value for _, value in points)
    pad = (high - low) * 0.15 or max(abs(high) * 0.1, 1)
    plot.yValueAxis.valueMin, plot.yValueAxis.valueMax = low - pad, high + pad
    plot.yValueAxis.labelTextFormat = _number
    plot.yValueAxis.labels.fontName = _REGULAR
    plot.yValueAxis.labels.fontSize = 7.5
    plot.yValueAxis.gridStrokeColor = LINE
    plot.yValueAxis.visibleGrid = True
    plot.yValueAxis.strokeColor = colors.white
    start, end = points[0][0], points[-1][0]
    plot.xValueAxis.valueMin, plot.xValueAxis.valueMax = start, end if end > start else start + 86400
    plot.xValueAxis.valueSteps = [start + (end - start) * step / 5 for step in range(6)]
    plot.xValueAxis.labelTextFormat = lambda moment: datetime.fromtimestamp(moment, UTC).strftime("%d.%m.%y")
    plot.xValueAxis.labels.fontName = _REGULAR
    plot.xValueAxis.labels.fontSize = 7.5
    plot.xValueAxis.strokeColor = LINE
    drawing.add(plot)
    return [Paragraph(caption, _BODY), drawing]


def _tolerance_chart(tolerance: dict[str, int], size: float) -> Drawing | None:
    parts = [
        (tolerance.get("suited", 0), "Подошло", MINT),
        (tolerance.get("unsuited", 0), "Не подошло", CORAL),
        (tolerance.get("unknown", 0), "Не оценено", LINE),
    ]
    parts = [part for part in parts if part[0]]
    if not parts:
        return None
    drawing = Drawing(size, size)
    pie = Pie()
    pie.x = pie.y = 4 * mm
    pie.width = pie.height = size - 8 * mm
    pie.data = [count for count, _, _ in parts]
    pie.labels = [str(count) for count, _, _ in parts]
    pie.simpleLabels = True
    pie.slices.strokeColor = colors.white
    pie.slices.strokeWidth = 1.5
    pie.slices.fontName = _BOLD
    pie.slices.fontSize = 9
    pie.slices.labelRadius = 0.65
    for index, (_, _, color) in enumerate(parts):
        pie.slices[index].fillColor = color
    drawing.add(pie)
    return drawing


def _food(report: PetReport, width: float) -> list:
    if not report.foods:
        return [Paragraph("Журнал питания пока пуст.", _SMALL)]
    rows = [["Корм", "Раз", "Понравился", "Подошёл", "Реакции"]]
    bad = []
    for index, food in enumerate(report.foods, start=1):
        rows.append([
            Paragraph(_text(food.name), _CELL),
            str(food.times),
            f"{food.liked} из {food.times}",
            f"{food.suited} из {food.times}",
            Paragraph(_text("; ".join(food.reactions)) or "—", _CELL),
        ])
        if food.unsuited:
            bad.append(index)
    table_width = width - 46 * mm
    table = _table(rows, [table_width - 106 * mm, 10 * mm, 22 * mm, 20 * mm, 54 * mm], highlight=bad)
    pie = _tolerance_chart(report.tolerance, 42 * mm)
    verdicts = (("suited", "подошло", MINT), ("unsuited", "не подошло", CORAL), ("unknown", "не оценено", LINE))
    legend_lines = [
        f"<font color='{color.hexval().replace('0x', '#')}'>■</font> {label}: {report.tolerance.get(key, 0)}"
        for key, label, color in verdicts
        if report.tolerance.get(key)
    ]
    side = [pie or "", Paragraph("<br/>".join(legend_lines), _SMALL)]
    layout = Table([[table, side]], colWidths=[table_width, 46 * mm])
    layout.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0)]))
    flow: list = [layout]
    if report.suspects:
        flow += [
            Spacer(1, 4),
            Paragraph(
                f"<b>Под подозрением:</b> {_text(', '.join(report.suspects))} — эти ингредиенты были в кормах, "
                "которые не подошли, и не встречались ни в одном подошедшем.",
                _BODY,
            ),
        ]
    return flow


def _wellbeing(report: PetReport, width: float) -> list:
    flow: list = []
    if report.scales:
        rows = [["Показатель", "Среднее за 90 дней", "Записей"]]
        for scale in report.scales:
            stars = "●" * round(scale.average) + "○" * (5 - round(scale.average))
            rows.append([scale.name, f"{stars}  {_number(scale.average)} из 5", str(scale.count)])
        flow.append(_table(rows, [width - 90 * mm, 60 * mm, 30 * mm]))
    if report.checks:
        rows = [["Наблюдение", "Сколько раз", "Последний раз"]]
        rows += [[check.name, str(check.count), _date(check.last)] for check in report.checks]
        flow += [Spacer(1, 6), _table(rows, [width - 90 * mm, 30 * mm, 60 * mm], highlight=list(range(1, len(rows))))]
    return flow


def _notes(report: PetReport) -> list:
    heading = Paragraph("Заключения врачей и заметки", _H2)
    if not report.notes:
        return [heading, Paragraph("Заключений и заметок пока нет.", _SMALL)]
    blocks = [
        [
            Paragraph(f"<b>{_date(note.moment)} · {_text(note.title)}</b>", _BODY),
            Paragraph(_text(note.text), _BODY),
            Spacer(1, 5),
        ]
        for note in report.notes
    ]
    # A note never splits across pages, and the heading always sits on top of the first one.
    return [KeepTogether([heading, *blocks[0]]), *(KeepTogether(block) for block in blocks[1:])]


def _footer(report: PetReport):
    def draw(canvas, document) -> None:
        canvas.saveState()
        canvas.setFont(_REGULAR, 8)
        canvas.setFillColor(MUTED)
        canvas.drawString(document.leftMargin, 10 * mm, f"PetCare · {report.pet_name} · {_date(report.generated_at)}")
        canvas.drawRightString(A4[0] - document.rightMargin, 10 * mm, f"стр. {document.page}")
        canvas.restoreState()

    return draw


def render_pdf(report: PetReport) -> bytes:
    _register_fonts()
    buffer = BytesIO()
    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=14 * mm,
        rightMargin=14 * mm,
        topMargin=12 * mm,
        bottomMargin=16 * mm,
        title=f"PetCare — {report.pet_name}",
        author="PetCare",
    )
    width = document.width
    story: list = [_header(report, width), Spacer(1, 5 * mm), _kpis(report, width)]
    alert = _alert(report, width)
    if alert is not None:
        story += [Spacer(1, 3 * mm), alert]
    story += [Paragraph("Ближайшие процедуры", _H2), *_upcoming(report, width)]
    story += [Paragraph("Прививки, обработки и лекарства", _H2), *_procedures(report, width)]
    chart = _activity_chart(report, width)
    if chart is not None:
        story.append(KeepTogether([Paragraph("Активность ухода за 12 месяцев", _H2), chart]))
    if report.series:
        charts = [_series_chart(series, width) for series in report.series]
        story.append(KeepTogether([Paragraph("Вес и показатели", _H2), *charts[0]]))
        story += [KeepTogether(chart) for chart in charts[1:]]
    wellbeing = _wellbeing(report, width)
    if wellbeing:
        story.append(KeepTogether([Paragraph("Самочувствие", _H2), *wellbeing]))
    story.append(KeepTogether([Paragraph("Питание", _H2), *_food(report, width)]))
    story += _notes(report)
    footer = _footer(report)
    document.build(story, onFirstPage=footer, onLaterPages=footer)
    return buffer.getvalue()


class ReportlabPetReportRenderer(PetReportRenderer):
    async def render(self, report: PetReport) -> bytes:
        # ReportLab is CPU-bound and synchronous: keep it off the event loop.
        return await anyio.to_thread.run_sync(render_pdf, report)
