from dishka import Provider, Scope, provide_all

from app.application.states.interactors import (
    CreateState,
    DeleteState,
    GetState,
    ListStates,
    SummarizeStates,
    UpdateState,
)


class StateProvider(Provider):
    scope = Scope.REQUEST
    interactors = provide_all(ListStates, GetState, CreateState, UpdateState, DeleteState, SummarizeStates)
