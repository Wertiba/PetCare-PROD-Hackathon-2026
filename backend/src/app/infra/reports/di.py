from dishka import Provider, Scope, provide

from app.application.ports.pet_report import PetReportRenderer
from app.infra.reports.pdf import ReportlabPetReportRenderer


class ReportRendererProvider(Provider):
    @provide(scope=Scope.APP)
    def renderer(self) -> PetReportRenderer:
        return ReportlabPetReportRenderer()
