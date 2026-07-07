class BookNotFoundError(Exception):
    def __init__(self, message="The requested book was not found in the database."):
        self.message = message
        super().__init__(self.message)