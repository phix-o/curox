import json
from typing import Any, cast

from fastapi import HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from starlette.responses import JSONResponse

from src.common.utils.responses import build_error_response


def handle_http_exception(_request: Request, exc):
    exc = cast(HTTPException, exc)

    headers = exc.headers or {}
    data_str = headers.get("X-Data")
    data: dict[str, Any] | None = None
    if data_str:
        data = json.loads(data_str)

    response = build_error_response(data, message=exc.detail).model_dump()

    print("\n::Error::")
    print(response)
    return JSONResponse(status_code=exc.status_code, content=response)


def handle_validation_error(_request: Request, exc):
    exc = cast(RequestValidationError, exc)
    response = build_error_response(exc.errors()).model_dump()

    return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=response)
