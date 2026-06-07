# mainapp/middleware.py

from mainapp.log_utils import create_log, get_ip

# এই path গুলো log হবে না (noise কমাতে)
SKIP_PATHS = [
    '/admin/jsi18n/',
    '/static/',
    '/media/',
    '/favicon.ico',
    '/erp-system-logs/',   # নিজের log endpoint log করবে না
]

# শুধু এই method গুলো log হবে
LOG_METHODS = ['POST', 'PUT', 'PATCH', 'DELETE']


class ERPAutoLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Skip করার শর্ত
        should_skip = any(
            request.path.startswith(p) for p in SKIP_PATHS
        )
        if should_skip:
            return response

        # শুধু authenticated user এবং নির্দিষ্ট method
        if (
            request.user.is_authenticated
            and request.method in LOG_METHODS
        ):
            status = response.status_code

            # Log level ঠিক করো
            if status >= 500:
                level = 'error'
            elif status >= 400:
                level = 'warning'
            else:
                level = 'info'

            # Action নাম বানাও
            action = f'{request.method} {request.path}'

            # Module বের করো path থেকে
            # e.g. /api/bookings/new/ → "bookings"
            parts = [p for p in request.path.split('/') if p]
            module = parts[1] if len(parts) > 1 else parts[0] if parts else 'system'

            create_log(
                action=action,
                module=module.upper(),
                user=request.user,
                description=f'Status: {status}',
                ip_address=get_ip(request),
                log_level=level,
            )

        return response