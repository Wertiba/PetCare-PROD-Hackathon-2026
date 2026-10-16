from uuid import uuid4

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.api.v1.exceptions import APIException, Conflict
from app.api.v1.exceptions.exc_map import DOMAIN_TO_API
from app.core.exceptions.base import DuplicateError, RepositoryError
from app.core.exceptions.user_exs import EntityError
from app.core.logger import Logger
from app.core.middleware.trace_id import get_trace_id
from app.core.schemas.responses import FieldError, ValidationErrorResponse
from app.core.utils import loc_to_field
from app.core.utils.loc2field import priority, rejected_value

logger = Logger.get_logger()


def _json(api_exc: APIException) -> JSONResponse:
    return JSONResponse(
        status_code=api_exc.status_code,
        content=api_exc.to_response().model_dump(exclude_none=True, mode="json"),
    )


def register_exception_handlers(app: FastAPI):
    @app.exception_handler(EntityError)
    async def handle_domain_exception(request: Request, exc: EntityError):  # noqa: RUF029
        factory = None
        for exc_cls, fac in DOMAIN_TO_API.items():
            if isinstance(exc, exc_cls):
                factory = fac
                break

        if factory:
            api_exc = factory(request.url.path, exc)  # noqa
        else:
            logger.warning("Unmapped domain error {} on {}", type(exc).__name__, request.url.path)
            api_exc = APIException(
                path=request.url.path,
                message="Domain error",
            )

        return _json(api_exc)

    @app.exception_handler(DuplicateError)
    async def handle_duplicate(request: Request, exc: DuplicateError):  # noqa: RUF029
        logger.info("Duplicate on {}: {}", request.url.path, exc)
        return _json(Conflict(path=request.url.path))

    @app.exception_handler(RepositoryError)
    async def handle_repository_error(request: Request, exc: RepositoryError):  # noqa: RUF029
        logger.opt(exception=exc).error("Database error on {} {}", request.method, request.url.path)
        return _json(APIException(path=request.url.path))

    @app.exception_handler(Exception)
    async def handle_unexpected(request: Request, exc: Exception):  # noqa: RUF029
        logger.opt(exception=exc).error("Unhandled error on {} {}", request.method, request.url.path)
        return _json(APIException(path=request.url.path))

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):  # noqa: RUF029
        field_errors = [
            FieldError(
                field=loc_to_field(tuple(err.get("loc", ()))),
                issue=err.get("msg"),
                rejectedValue=rejected_value(err),
            )
            for err in sorted(exc.errors(), key=priority)
        ]

        payload = ValidationErrorResponse(
            traceId=get_trace_id() or str(uuid4()),
            path=request.url.path,
            fieldErrors=field_errors,
        )

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content=payload.model_dump(mode="json"),
        )
