# mainapp/log_utils.py

def create_log(
    action,
    module,
    user=None,
    description='',
    ip_address=None,
    log_level='info',
):
    """
    যেকোনো জায়গা থেকে call করা যাবে।
    Circular import এড়াতে ভেতরে import করা হয়েছে।
    """
    try:
        from mainapp.models import ERPSystemLog
        ERPSystemLog.objects.create(
            user=user,
            action=action,
            module=module,
            description=description,
            ip_address=ip_address,
            log_level=log_level,
        )
    except Exception as e:
        # Log fail হলে পুরো system crash করবে না
        print(f'[LOG ERROR] {e}')


def get_ip(request):
    """Request থেকে real IP বের করে।"""
    x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded:
        return x_forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')