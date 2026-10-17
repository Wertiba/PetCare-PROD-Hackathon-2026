from dishka import Provider, Scope, provide_all

from app.application.events.interactors import (
    CompleteEvent,
    CreateEvent,
    DeleteEvent,
    GetEvent,
    ListEvents,
    ListUpcomingEvents,
    UpdateEvent,
)


class EventProvider(Provider):
    scope = Scope.REQUEST
    interactors = provide_all(
        ListEvents, ListUpcomingEvents, GetEvent, CreateEvent, UpdateEvent, CompleteEvent, DeleteEvent
    )
