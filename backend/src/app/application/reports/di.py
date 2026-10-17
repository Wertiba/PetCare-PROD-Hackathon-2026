from dishka import Provider, Scope, provide_all

from app.application.reports.interactors import ExportPetReport


class ReportProvider(Provider):
    scope = Scope.REQUEST
    interactors = provide_all(ExportPetReport)
