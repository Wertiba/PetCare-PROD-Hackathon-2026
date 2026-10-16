import time

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Match

from app.core.logger import Logger
from app.core.metrics import HTTP_REQUEST_DURATION_SECONDS, HTTP_REQUESTS_IN_PROGRESS, HTTP_REQUESTS_TOTAL

logger = Logger.get_logger()

_QUIET_PREFIXES = ("/health", "/metrics")
_UNMATCHED = "<unmatched>"


def _route_template(request: Request) -> str:
    """Route path like /api/v1/pets/{pet_id}: keeps metric label cardinality bounded."""
    for route in request.app.router.routes:
        match, _ = route.matches(request.scope)
        if match == Match.FULL:
            return getattr(route, "path", _UNMATCHED)
    return _UNMATCHED


class ObservabilityMiddleware(BaseHTTPMiddleware):
    """Prometheus request metrics plus one access-log line per request."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        path = request.url.path
        if path == "/metrics":
            return await call_next(request)

        method = request.method
        template = _route_template(request)
        status_code = 500
        started = time.perf_counter()
        HTTP_REQUESTS_IN_PROGRESS.labels(method=method).inc()
        try:
            response = await call_next(request)
            status_code = response.status_code
            return response
        finally:
            elapsed = time.perf_counter() - started
            HTTP_REQUESTS_IN_PROGRESS.labels(method=method).dec()
            HTTP_REQUESTS_TOTAL.labels(method=method, path=template, status=str(status_code)).inc()
            HTTP_REQUEST_DURATION_SECONDS.labels(method=method, path=template).observe(elapsed)
            if not path.startswith(_QUIET_PREFIXES):
                logger.info("{} {} -> {} in {:.1f} ms", method, path, status_code, elapsed * 1000)
