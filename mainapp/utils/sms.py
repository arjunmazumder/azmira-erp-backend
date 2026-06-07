import requests
from django.conf import settings


def send_sms(phone, message):

    # ✅ DEBUG mode এ আসল SMS যাবে না, শুধু print হবে
    if settings.DEBUG:
        print(f"[SMS DEBUG] To: {phone}")
        print(f"[SMS DEBUG] Message: {message}")
        return True, None

    if not phone:
        return False, "Phone number is empty"

    try:
        response = requests.post(
            'https://sms.sslwireless.com/pushapi/dynamic/server.php',
            data={
                'apitoken': settings.SSL_WIRELESS_API_TOKEN,
                'sid':      settings.SSL_WIRELESS_SENDER_ID,
                'msisdn':   phone,
                'msg':      message,
                'csmsid':   f'sms_{phone}_{int(__import__("time").time())}',
            },
            timeout=10
        )

        if not response.text:
            return False, "Empty response from SSL Wireless"

        data = response.json()
        if data.get('status') == 'SUCCESS':
            return True, None
        return False, data.get('message', 'Unknown error')

    except Exception as e:
        return False, str(e)