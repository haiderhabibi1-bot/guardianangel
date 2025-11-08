import time
from django.http import HttpResponseTooManyRequests
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin

class SimpleRateLimitMiddleware(MiddlewareMixin):
    """
    A simple in-memory rate limiter.
    Example default: "60:8" -> 8 requests per 60 seconds per IP.
    Not bulletproof (memory resets when app restarts), but good for basic spam protection.
    """

    cache = {}

    def process_request(self, request):
        # Skip admin and static
        path = request.path
        if path.startswith('/static') or path.startswith('/admin'):
            return None

        limit_str = getattr(settings, "RATELIMIT_DEFAULT", "60:8")
        seconds, max_requests = map(int, limit_str.split(":"))

        ip = self.get_client_ip(request)
        now = time.time()

        # Initialize record
        rec = self.cache.get(ip, [])
        rec = [t for t in rec if now - t < seconds]  # keep only recent timestamps
        rec.append(now)
        self.cache[ip] = rec

        if len(rec) > max_requests:
            return HttpResponseTooManyRequests("Too many requests. Please slow down.")

        return None

    def get_client_ip(self, request):
        xff = request.META.get("HTTP_X_FORWARDED_FOR")
        if xff:
            ip = xff.split(",")[0].strip()
        else:
            ip = request.META.get("REMOTE_ADDR", "")
        return ip
