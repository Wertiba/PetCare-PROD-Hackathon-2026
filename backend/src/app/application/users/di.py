from dishka import Provider, Scope, provide_all

from app.application.users.interactors import GetMe, UpdateMe


class UserProvider(Provider):
    scope = Scope.REQUEST
    interactors = provide_all(GetMe, UpdateMe)
