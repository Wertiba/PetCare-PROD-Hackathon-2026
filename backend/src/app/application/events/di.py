from dishka import Provider, Scope, provide_all

from app.application.events.interactors import (
    CompleteEvent,
    CreateEvent,
    DeleteEvent,
    ExportEventsCalendar,
    GetEvent,
    ListEvents,
    ListUpcomingEvents,
    UpdateEvent,
)


class EventProvider(Provider):
    scope = Scope.REQUEST
    interactors = provide_all(
        ListEvents,
        ListUpcomingEvents,
        ExportEventsCalendar,
        GetEvent,
        CreateEvent,
        UpdateEvent,
        CompleteEvent,
        DeleteEvent,
    )
