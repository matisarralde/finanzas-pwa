# apps/backend/src/core/errors.py
from fastapi import status

class AppException(Exception):
    def __init__(self, detail: str, status_code: int = status.HTTP_400_BAD_REQUEST, error_code: str = "APP_ERROR"):
        self.detail = detail
        self.status_code = status_code
        self.error_code = error_code
        super().__init__(detail)

class NotFoundError(AppException):
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(detail, status.HTTP_404_NOT_FOUND, "NOT_FOUND")

class DuplicateError(AppException):
    def __init__(self, detail: str = "Resource already exists"):
        super().__init__(detail, status.HTTP_409_CONFLICT, "DUPLICATE")

class ValidationError(AppException):
    def __init__(self, detail: str):
        super().__init__(detail, status.HTTP_422_UNPROCESSABLE_ENTITY, "VALIDATION_ERROR")
