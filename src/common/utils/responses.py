from typing import Any, Generic, TypeVar, cast

from pydantic import BaseModel, Field

T = TypeVar("T")


class CustomResponse(BaseModel, Generic[T]):
    """
    Holds all the api response formats
    """

    error: bool = Field(description="Status of the resposne")
    message: str = Field(description="Short message that describes the response")
    data: T = Field(description="The response data")

    def model_dump(self, *args, **kwargs):
        dump = super().model_dump(*args, **kwargs)
        if dump["data"] is None:
            dump.pop("data")

        return dump


def build_response(data: T, message: str = "Success") -> CustomResponse[T]:
    return CustomResponse(error=False, message=message, data=data)


def build_error_response(
    data: T, message: str = "An error occured"
) -> CustomResponse[T]:
    return CustomResponse(error=True, message=message, data=data)
