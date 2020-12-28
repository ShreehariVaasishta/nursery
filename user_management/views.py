from datetime import datetime, timedelta
from functools import partial

import jwt
from django.conf import settings
from django.contrib.auth.hashers import check_password, make_password
from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from rest_framework import status as stat_code
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from common_utils.custom_auth import TokenAuthentication, generate_token
from common_utils.permissions import IsNurseryUser, IsBuyerUser
from common_utils.response import response

from .models import Nursery, Buyer
from .serializers import BuyerSerializer, NurserySerializer

# Create your views here.


class BuyerRegisterationApiView(APIView):
    """
    post:
    create buyer user
    """

    permission_classes = (AllowAny,)
    serializer_class = BuyerSerializer

    def post(self, request):
        try:
            if "middle_name" not in request.data:
                request.data["middle_name"] = ""
            if "last_name" not in request.data:
                request.data["last_name"] = ""
            user = Buyer.objects.create(
                email=request.data["email"],
                password=make_password(request.data["password"]),
                first_name=request.data["first_name"],
                middle_name=request.data["middle_name"],
                last_name=request.data["last_name"],
            )
            # Do no return user data on successful registration
            return response(status_code=stat_code.HTTP_200_OK, status=True, msg="User(Buyer) registered successfully.")
        except IntegrityError as ie:
            return response(
                status_code=stat_code.HTTP_403_FORBIDDEN,
                status=False,
                msg="User(Buyer) with this email already exist.",
            )
        except Exception as e:
            return response(status_code=stat_code.HTTP_403_FORBIDDEN, status=False, msg=str(e))


class NurseryRegisterationApiView(APIView):
    """
    post:
    create nursery user
    """

    permission_classes = (AllowAny,)
    serializer_class = BuyerSerializer

    def post(self, request):
        try:
            if "about" not in request.data:
                request.data["about"] = ""
            user = Nursery.objects.create(
                email=request.data["email"],
                password=make_password(request.data["password"]),
                name=request.data["name"],
                about=request.data["about"],
            )
            # Do no return user data on successful registration
            return response(
                status_code=stat_code.HTTP_200_OK, status=True, msg="User(Nursery) registered successfully."
            )
        except IntegrityError as ie:
            return response(
                status_code=stat_code.HTTP_403_FORBIDDEN,
                status=False,
                msg="User(Nursery) with this email exists.",
            )
        except Exception as e:
            return response(status_code=stat_code.HTTP_403_FORBIDDEN, status=False, msg=str(e))


class BuyerLoginApiView(APIView):
    """
    post:
    login user and return jwt token
    """

    permission_classes = (AllowAny,)

    def post(self, request):
        try:
            user = Buyer.objects.only("email").get(email=request.data["email"])
            password_matched = check_password(request.data["password"], user.password)
            if password_matched:
                user_type = "buyer"
                jwt_token = generate_token(user.id.urn, user_type)
                data = {"user_id": user.id, "jwt_token": jwt_token}
                return response(
                    status_code=stat_code.HTTP_200_OK, status=True, msg="User logged in successfully.", data=data
                )
            return response(
                status_code=stat_code.HTTP_401_UNAUTHORIZED, status=False, msg="Invalid Credentials.", data=[]
            )
        except Buyer.DoesNotExist as ude:
            return response(status_code=stat_code.HTTP_403_FORBIDDEN, status=False, msg="User does not exist.")
        except Exception as e:
            return response(status_code=stat_code.HTTP_403_FORBIDDEN, status=False, msg=str(e))


class NurseryLoginApiView(APIView):
    """
    post:
    login user and return jwt token
    """

    def post(self, request):
        try:

            user = Nursery.objects.only("email", "id").get(email=request.data["email"])
            password_matched = check_password(request.data["password"], user.password)
            if password_matched:
                user_type = "nursery"
                jwt_token = generate_token(user.id.urn, user_type)
                data = {"user_id": user.id, "jwt_token": jwt_token}
                return response(
                    status_code=stat_code.HTTP_200_OK, status=True, msg="User logged in successfully.", data=data
                )
            return response(
                status_code=stat_code.HTTP_401_UNAUTHORIZED, status=False, msg="Invalid Credentials.", data=[]
            )
        except Buyer.DoesNotExist as ude:
            return response(status_code=stat_code.HTTP_403_FORBIDDEN, status=False, msg="User does not exist.")
        except Exception as e:
            return response(status_code=stat_code.HTTP_403_FORBIDDEN, status=False, msg=str(e))


class BuyerRetreiveUpdateDeleteApiView(APIView):
    """
    get:
    returns user details

    put:
    update user details

    delete:
    delete user
    """

    authentication_classes = (TokenAuthentication,)

    def get(self, request):
        try:
            user = Buyer.objects.get(pk=request.user.id)
            serialized = BuyerSerializer(user).data
            return response(
                status_code=stat_code.HTTP_200_OK, status=True, msg="Retrieved user data.", data=serialized
            )
        except Buyer.DoesNotExist as ude:
            return response(status_code=stat_code.HTTP_403_FORBIDDEN, status=False, msg="User does not exist.")
        except Exception as e:
            return response(status_code=stat_code.HTTP_403_FORBIDDEN, status=False, msg=str(e))

    def put(self, request):
        try:
            user = get_object_or_404(Buyer.objects.all(), pk=request.user.id)
            if "password" in request.data:
                del request.data["password"]
            if "email" in request.data:
                del request.data["email"]
            if "isdeactivated" in request.data:
                del request.data["isdeactivated"]
            if "created_at" in request.data:
                del request.data["created_at"]
            serializer_class = BuyerSerializer(user, request.data, partial=True)  # accepts partial update
            if serializer_class.is_valid(raise_exception=True):
                serializer_class.save()
                data = serializer_class.data
                return response(status_code=stat_code.HTTP_200_OK, status=True, msg="Retrieved user data.", data=data)
            return response(status_code=stat_code.HTTP_403_FORBIDDEN, status=False, msg=serializer_class.errors)
        except Buyer.DoesNotExist as ude:
            return response(status_code=stat_code.HTTP_403_FORBIDDEN, status=False, msg="User does not exist.")
        except Exception as e:
            return response(status_code=stat_code.HTTP_403_FORBIDDEN, status=False, msg=str(e))

    def delete(self, request):
        try:
            """
            User will not be deleted from the database unless we do regular backup of database.
            if need to be deleted, call delete() method instead of update()

            user_delete = Buyer.objects.filter(pk=request.user.id).delete()
            """
            user_delete = Buyer.objects.filter(pk=request.user.id).update(isdeleted=True)
            return response(status_code=stat_code.HTTP_200_OK, status=True, msg="User deleted successfully.")
        except Buyer.DoesNotExist as ude:
            return response(status_code=stat_code.HTTP_403_FORBIDDEN, status=False, msg="User does not exist.")
        except Exception as e:
            return response(status_code=stat_code.HTTP_403_FORBIDDEN, status=False, msg=str(e))


class NurseryRetreiveUpdateDeleteApiView(APIView):
    """
    get:
    returns user details

    put:
    update user details

    delete:
    delete user
    """

    authentication_classes = (TokenAuthentication,)

    def get(self, request):
        try:
            user = Nursery.objects.get(pk=request.user.id)
            serialized = NurserySerializer(user).data
            return response(
                status_code=stat_code.HTTP_200_OK, status=True, msg="Retrieved user data.", data=serialized
            )
        except Nursery.DoesNotExist as ude:
            return response(status_code=stat_code.HTTP_403_FORBIDDEN, status=False, msg="User does not exist.")
        except Exception as e:
            return response(status_code=stat_code.HTTP_403_FORBIDDEN, status=False, msg=str(e))

    def put(self, request):
        try:
            user = get_object_or_404(Nursery.objects.all(), pk=request.user.id)
            if "ratings" in request.data:
                del request.data["ratings"]
            if "email" in request.data:
                del request.data["email"]
            if "password" in request.data:
                del request.data["password"]
            if "isdeactivated" in request.data:
                del request.data["isdeactivated"]
            if "created_at" in request.data:
                del request.data["created_at"]
            if (
                "name" in request.data
            ):  # Nursery names should not be changed. Should be changed only through some kind of verification.
                del request.data["name"]
            serializer_class = NurserySerializer(user, request.data, partial=True)  # accepts partial update
            if serializer_class.is_valid(raise_exception=True):
                serializer_class.save()
                data = serializer_class.data
                return response(status_code=stat_code.HTTP_200_OK, status=True, msg="Retrieved user data.", data=data)
            return response(status_code=stat_code.HTTP_403_FORBIDDEN, status=False, msg=serializer_class.errors)
        except Nursery.DoesNotExist as ude:
            return response(status_code=stat_code.HTTP_403_FORBIDDEN, status=False, msg="User does not exist.")
        except Exception as e:
            return response(status_code=stat_code.HTTP_403_FORBIDDEN, status=False, msg=str(e))

    def delete(self, request):
        try:
            """
            User will not be deleted from the database unless we do regular backup of database.
            if need to be deleted, call delete() method instead of update()

            user_delete = Nursery.objects.filter(pk=request.user.id).delete()
            """
            user_delete = Nursery.objects.filter(pk=request.user.id).update(isdeleted=True)
            return response(status_code=stat_code.HTTP_200_OK, status=True, msg="User deleted successfully.")
        except Nursery.DoesNotExist as ude:
            return response(status_code=stat_code.HTTP_403_FORBIDDEN, status=False, msg="User does not exist.")
        except Exception as e:
            return response(status_code=stat_code.HTTP_403_FORBIDDEN, status=False, msg=str(e))
