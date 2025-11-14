import json

from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder


class CustomHTTPException(HTTPException):
    def __init__(
        self,
        status_code: int,
        detail: str,
        data: dict[str, str] | None = None,
    ) -> None:
        headers: dict[str, str] | None = None
        if data:
            headers = {"X-Data": json.dumps(jsonable_encoder(data))}

        super().__init__(status_code, detail, headers)


class BadRequestException(CustomHTTPException):
    def __init__(
        self, detail="Invalid request", data: dict[str, str] | None = None
    ) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST, detail=detail, data=data
        )


class NotFoundException(HTTPException):
    def __init__(
        self,
        detail="The resource with the given id does not exist",
    ) -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
        )


class UnauthorisedException(HTTPException):
    def __init__(self, detail="You do not have permission to proceed"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


class UniqueValidationError(HTTPException):
    def __init__(self, detail="This record does not satisfy constraints"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)
