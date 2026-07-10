from fastapi import HTTPException, status


# ==========================================
# 1. Web Layer Exceptions 
# ==========================================

class CredentialsException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},)

class PermissionDeniedException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action"
        )

# ==========================================
# 2. Service Layer Exceptions 
# ==========================================

class BookNotFoundException(Exception):
    def __init__(self, message="The requested book was not found in the database."):
        self.message = message
        super().__init__(self.message)

class BookNotAvailableException(Exception):
    def __init__(self):
        super().__init__("This book is currently rented out.")

class TooLongRentalDaysException(Exception):
    def __init__(self, message="The number of rental's days are too big, max 365 days"):
        self.message = message
        super().__init__(self.message)

class UserHasOverdueBooksException(Exception):
    def __init__(self, message="Please return your books to booked previously"):
        self.message=message
        super().__init__(self.message)

class RentalNotFoundException(Exception):
    def __init__(self, message="We were not able find your rental"):
        self.message = message
        super().__init__(self.message)
    
class BookAlreadyReturnedException(Exception):
        def __init__(self, message="Book is already returned"):
            self.message = message
            super().__init__(self.message)

class MaxRentalsReachedException(Exception):
        def __init__(self, message="Maximum number of books were rented"):
            self.message = message
            super().__init__(self.message)
