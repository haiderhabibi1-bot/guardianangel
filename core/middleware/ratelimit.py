import time
from django.http import HttpResponse
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin

class SimpleRateLimitMiddleware(MiddlewareMixin):
    """
    A simple in-memory rate limiter.

    Default format (from settings.RATELIMIT_DEFAULT):
        "60:8" -> 8 requests per 60 seconds per IP.

    Not persistent across restarts, but good enough
    for basic abuse protection on a small deployment.
    """

    cache = {}

    def process_request(self, request):
        path = request.path

        # Skip static files and admin (optional)
        if path.startswith('/static') or path.startswith('/admin'):
            return None

        # Read limit from settings, fallback to 8 req / 60s
        limit_str = getattr(settings, "RATELIMIT_DEFAULT", "60:8")
        try:
            seconds, max_requests = map(int, limit_str.split(":"))
        except ValueError:
            seconds, max_requests = 60, 8

        ip = self.get_client_ip(request)
        now = time.time()

        # Get existing timestamps for this IP and drop old ones
        timestamps = self.cache.get(ip, [])
        timestamps = [t for t in timestamps if now - t < seconds]
        timestamps.append(now)
        self.cache[ip] = timestamps

        if len(timestamps) > max_requests:
            # 429 Too Many Requests (compatible with all Django versions)
            return HttpResponse(
                "Too many requests. Please slow down.",
                status=429
            )

        return None

    def get_client_ip(self, request):
        xff = request.META.get("HTTP_X_FORWARDED_FOR")
        if xff:
            return xff.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR", "") or "unknown"
