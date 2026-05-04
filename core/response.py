from rest_framework.response import Response


def success_response(message, data, status_code=200):
    return Response({
        "message": message,
        "data": {
            "requests": data
        }
    }, status=status_code)


def error_response(message, errors, status_code=400):
    return Response({
        "message": message,
        "data": {
            "requests": [errors]
        }
    }, status=status_code)