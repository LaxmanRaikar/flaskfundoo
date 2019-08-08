


class Note(Exception):

    def __init__(self):
        # initialize the default params
        # pagination params start with 0, limit 10, page number display
        # link, text, image, checklist using tuples
        pass

    def add(self, **kwargs):
        # calling the models to add note
        pass

    def get(self, noteId):
        pass

    def pin(self, noteId):
        pass

    def unPin(self, noteId):
        pass

    def updateTitleDescription(self, **kwargs):
        pass

    def archive(self, noteId):
        pass

    def trash(self, noteId):
        pass

    def getAll(self, query):
        # userId (Mandatory), isArchive, isPinned, isTrash
        pass

    def delete(self, query):
        # userId (Mandatory), isArchive, isPinned, isTrash
        pass


