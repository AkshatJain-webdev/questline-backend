from typing import Self

from fastapi import Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError


class AppError(Exception):
    status_code: int = 500
    code: str = "internal_error"


class NotFoundError(AppError):
    status_code = 404
    code = "not_found"


# Well-formed, but breaks a rule: a duplicate, a cycle, or an inconsistent tree.
class ConflictError(AppError):
    status_code = 409
    code = "conflict"


# The requested changes would leave the document invalid, e.g. a required field set to null.
class InvalidError(AppError):
    status_code = 422
    code = "invalid"

    @classmethod
    def from_validation_error(cls, error: ValidationError) -> Self:
        issues = (f"{'.'.join(map(str, issue['loc']))}: {issue['msg']}" for issue in error.errors())
        return cls("; ".join(issues))


async def handle_app_error(request: Request, error: AppError) -> JSONResponse:
    return JSONResponse(
        status_code=error.status_code, content={"code": error.code, "detail": str(error)}
    )
