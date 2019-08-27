from models import Notes
from app import db


class Note():

    def __init__(self, title=None, description=None, user_id=None, remainder=None, is_pinned=None, is_archive=None,
                 color=None, image=None, label=None, collabrator=None):
        self.title = title
        self.description = description
        self.user_id = user_id
        self.remainder = remainder
        self.is_pinned = is_pinned
        self.is_archive = is_archive
        self.color = color
        self.image = image
        self.label = label
        self.collabrator = collabrator

    def add(self):
        # calling the models to add note
        data = Notes(self.title, self.description, self.user_id, self.remainder, self.is_pinned, self.color,
               self.image, self.label, self.collabrator)
        print(data)


    def get(self, noteId):
        pass

    def pin(self, noteId):
        pass

    def unPin(self, noteId):
        pass

    def updateTitleDescription(self, id):
        print(self.title, self.description, id)
        if self.title and self.description is not None:
            note = Notes.query.get(id)
            note.title = self.title
            note.description = self.description
            db.session.commit()
            return True
        else:
            return False


    def archive(self, noteId):
        pass

    def trash(self, noteId):
        pass

    def getAll(self, query):
        # userId (Mandatory), isArchive, isPinned, isTrash
        pass

    def delete(self, id):
        # userId (Mandatory), isArchive, isPinned, isTrash
        delete_note = Notes.query.get(id)
        Notes.delete_data(delete_note)
        return True


