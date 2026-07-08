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

class BookNotFoundError(Exception):
    def __init__(self, message="The requested book was not found in the database."):
        self.message = message
        super().__init__(self.message)
