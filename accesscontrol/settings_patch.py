# settings.py এ এই অংশগুলো add/update করুন
# =====================================================

REST_FRAMEWORK = {
    # ← Custom JWT Authentication
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'api.authentication.ERPJWTAuthentication',
    ],
    # ← Default: login ছাড়া কেউ access করতে পারবে না
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
}

# JWT token config
from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME':  timedelta(hours=8),   # 8 ঘন্টা
    'REFRESH_TOKEN_LIFETIME': timedelta(days=30),   # 30 দিন
    'ROTATE_REFRESH_TOKENS':  True,
    'AUTH_HEADER_TYPES':      ('Bearer',),
}
