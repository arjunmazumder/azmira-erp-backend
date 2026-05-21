# api/authentication.py
# =====================================================
# JWT → ERPUser connection
# =====================================================

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken
from mainapp.models import ERPUser


class ERPJWTAuthentication(JWTAuthentication):
    """
    SimpleJWT কে ERPUser এর সাথে connect করে।
    Token এ erp_user_id রাখা হয়।
    """

    def get_user(self, validated_token):
        erp_user_id = validated_token.get('erp_user_id')
        if not erp_user_id:
            return None

        try:
            erp_user = ERPUser.objects.get(id=erp_user_id, is_active=True)
            # Django user object এ erp_user attach করা
            return ERPUserProxy(erp_user)
        except ERPUser.DoesNotExist:
            return None


class ERPUserProxy:
    """
    DRF এর request.user এর জন্য proxy class।
    ERPUser কে Django user এর মতো behave করায়।
    """

    def __init__(self, erp_user):
        self.erp_user = erp_user
        self.is_authenticated = True
        self.is_active = erp_user.is_active
        self.id = erp_user.id

    def __str__(self):
        return self.erp_user.username


def get_tokens_for_erp_user(erp_user):
    """
    ERPUser এর জন্য JWT token generate করা।
    views.py এর login function এ use করুন।
    """
    refresh = RefreshToken()
    refresh['erp_user_id'] = erp_user.id
    refresh['username'] = erp_user.username
    refresh['roles'] = erp_user.roles or []

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }
