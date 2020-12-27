import json

import jwt
from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse, request
from rest_framework import exceptions, status
from rest_framework.authentication import BaseAuthentication, get_authorization_header

from user_management.models import Buyer, Nursery


class TokenAuthentication(BaseAuthentication):
    model = None

    def get_model(self, user_type):
        model = {"buyer": Buyer, "nursery": Nursery}
        return model[user_type]

    def authenticate(self, request):

        auth = get_authorization_header(request).split()
        if not auth or auth[0].lower() != b"bearer":
            msg = "Invalid token header."
            raise exceptions.AuthenticationFailed(msg)

        lauth = len(auth)

        if lauth == 1:
            msg = "Invalid token header. No credentials provided."
            raise exceptions.AuthenticationFailed(msg)
        elif lauth > 2:
            msg = "Invalid token header"
            raise exceptions.AuthenticationFailed(msg)

        try:
            token = auth[1]
            if token == "null":
                msg = "Null token not allowed"
                raise exceptions.AuthenticationFailed(msg)
        except UnicodeError:
            msg = "Invalid token header. Token string should not contain invalid characters."
            raise exceptions.AuthenticationFailed(msg)

        return self.authenticate_credentials(token)

    def authenticate_credentials(self, token):

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            userid = payload["user_id"]
            model = self.get_model(payload["user_type"])

            try:
                user = Buyer.objects.get(id=userid)
            except Buyer.DoesNotExist:
                user = Nursery.objects.get(id=userid)
            except Nursery.DoesNotExist:
                raise exceptions.AuthenticationFailed({"error": "invalid_User_Token"})

        except jwt.exceptions.DecodeError:
            raise exceptions.AuthenticationFailed({"error": "Invalid_Token"})
        except jwt.exceptions.InvalidSignatureError:
            raise exceptions.AuthenticationFailed({"error": "Invalid_Signature"})
        except jwt.exceptions.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed({"error": "Token_Expired"})
        except jwt.exceptions.InvalidAudienceError:
            raise exceptions.AuthenticationFailed({"error": "Invalid_Token_Audience"})
        except jwt.exceptions.InvalidKeyError:
            raise exceptions.AuthenticationFailed({"error": "Invalid_Token_Key"})
        except jwt.exceptions.InvalidTokenError:
            raise exceptions.AuthenticationFailed({"error": "Invalid_Token_Error"})

        except Exception as e:
            raise exceptions.AuthenticationFailed({"error": e.args})

        return (user, None)

    def authenticate_header(self, request):
        return "Token"


def generate_token(id, user_type):
    payload = {
        "user_id": id,
        "user_type": user_type,
        "exp": settings.JWT_AUTH["JWT_EXPIRATION_DELTA"],
    }
    jwt_token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
    return jwt_token
