import time

import structlog

logger = structlog.get_logger("http_requests")

class AccessLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start = time.monotonic()
        response = self.get_response(request)
        duration = (time.monotonic() - start) * 1000  # ms

        logger.info(
            "request",
            method=request.method,
            path=request.get_full_path(),
            status=response.status_code,
            authorization=str(request.headers.get("Authorization", None)),
            user_agent=str(request.headers.get("User-Agent", None)),
            latency_ms=round(duration, 2),
        )
        return response
