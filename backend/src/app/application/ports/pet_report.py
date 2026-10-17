from typing import Protocol

from app.application.reports.dto import PetReport


class PetReportRenderer(Protocol):
    async def render(self, report: PetReport) -> bytes:
        """The report as a ready-to-download PDF document."""
        ...
