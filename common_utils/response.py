from rest_framework.response import Response


def response(status_code, status, msg, data=[]):
    return Response({"status": status, "message": msg, "data": data}, status_code)
