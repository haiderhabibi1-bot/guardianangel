from django.conf import settings
from django.utils.deprecation import MiddlewareMixin

class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Adds strong HTTP security headers to every response.
    These work together with the SECURE_* settings in settings.py.
    """

    def process_response(self, request, response):
        # Prevent framing (click-jacking)
        response.setdefault("X-Frame-Options", "DENY")

        # XSS protection
        response.setdefault("X-XSS-Protection", "1; mode=block")

        # MIME-sniffing protection
        response.setdefault("X-Content-Type-Options", "nosniff")

        # Referrer policy
        response.setdefault(
            "Referrer-Policy",
            getattr(settings, "SECURE_REFERRER_POLICY", "strict-origin-when-cross-origin"),
        )

        # Content Security Policy (CSP)
        csp = getattr(settings, "CSP_DEFAULT_SRC", ("'self'",))
        script_src = getattr(settings, "CSP_SCRIPT_SRC", ("'self'",))
        style_src = getattr(settings, "CSP_STYLE_SRC", ("'self'",))
        img_src = getattr(settings, "CSP_IMG_SRC", ("'self'",))
        connect_src = getattr(settings, "CSP_CONNECT_SRC", ("'self'",))

        # Combine to one header
        csp_directives = [
            f"default-src {' '.join(csp)};",
            f"script-src {' '.join(script_src)};",
            f"style-src {' '.join(style_src)};",
            f"img-src {' '.join(img_src)};",
            f"connect-src {' '.join(connect_src)};",
        ]
        response.setdefault("Content-Security-Policy", " ".join(csp_directives))

        return response
