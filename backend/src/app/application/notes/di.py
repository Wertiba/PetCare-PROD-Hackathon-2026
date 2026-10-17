from dishka import Provider, Scope, provide_all

from app.application.notes.interactors import CreateNote, DeleteNote, GetNote, ListNotes, UpdateNote


class NoteProvider(Provider):
    scope = Scope.REQUEST
    interactors = provide_all(ListNotes, GetNote, CreateNote, UpdateNote, DeleteNote)
