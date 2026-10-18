import uuid
from contextvars import ContextVar

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from app.infra.logger import log_trace_id

TRACE_ID_HEADER = "X-Trace-Id"

_trace_id_ctx: ContextVar[str] = ContextVar("trace_id", default="")


def get_trace_id() -> str:
    return _trace_id_ctx.get()


class TraceIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        trace_id = request.headers.get(TRACE_ID_HEADER) or str(uuid.uuid4())
        token = _trace_id_ctx.set(trace_id)
        # Keep the public header contract; arbitrary client text is never logged.
        try:
            safe_trace_id = uuid.UUID(trace_id)
        except ValueError:
            safe_trace_id = uuid.uuid4()
        log_token = log_trace_id.set(safe_trace_id)
        try:
            response = await call_next(request)
        finally:
            _trace_id_ctx.reset(token)
            log_trace_id.reset(log_token)
        response.headers[TRACE_ID_HEADER] = trace_id
        return response
