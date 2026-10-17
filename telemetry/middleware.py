from django.utils import timezone
from .models import AccessLog


def get_client_ip(request):
    """
    Extracts the client's real IP address from HTTP headers or remote address.
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip or '127.0.0.1'


class VisitorIPLoggingMiddleware:
    """
    Middleware that records the IP address and timestamp of every visitor
    accessing the website, replacing the need for guest passwords/logins.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Do not log static files, media, or favicon requests
        path = request.path
        if not (
            path.startswith('/static/')
            or path.startswith('/staticfiles/')
            or path.startswith('/media/')
            or path.startswith('/favicon.ico')
        ):
            try:
                ip = get_client_ip(request)
                user = request.user if getattr(request, 'user', None) and request.user.is_authenticated else None
                AccessLog.objects.create(
                    ip_address=ip,
                    path=path[:255],
                    method=request.method[:10],
                    user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
                    user=user,
                )
            except Exception:
                # Never disrupt user traffic if logging encounters a database lock
                pass

        return response
