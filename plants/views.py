from django.shortcuts import get_object_or_404
from rest_framework import status as stat_code
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from common_utils.custom_auth import TokenAuthentication, generate_token
from common_utils.permissions import IsNurseryUser, IsBuyerUser
from common_utils.response import response

from .models import Plants
from .serializers import PlantsSerializer

# Create your views here.
class PostListPlantsApiView(APIView):
    """
    post:
    post new plants

    get:
    returns list of plants posted by the requesting user
    """

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsNurseryUser,)

    def post(self, request):
        try:
            print(request.user.id, "<<<<<<<<<<<<<")
            if "image" not in request.data:
                request.data["image"] = None
            instances = Plants.objects.create(
                name=request.data["name"],
                owner_id=request.user.id,
                image=request.data["image"],
                plant_description=request.data["plant_description"],
                price=request.data["price"],
                inStock=request.data["inStock"],
            )
            serialized = PlantsSerializer(instances).data
            return response(
                status_code=stat_code.HTTP_200_OK,
                status=True,
                msg="Plant posted successfully.",
                data=serialized,
            )
        except Exception as e:
            return response(status_code=stat_code.HTTP_403_FORBIDDEN, status=False, msg=str(e))

    def get(self, request):
        try:
            instances = Plants.objects.filter(owner_id=request.user.id).exclude(isDeleted=True)
            serialized = PlantsSerializer(instances, many=True).data
            return response(
                status_code=stat_code.HTTP_200_OK,
                status=True,
                msg="Retreived list of plants.",
                data=serialized,
            )
        except Exception as e:
            return response(status_code=stat_code.HTTP_403_FORBIDDEN, status=False, msg=str(e))


class ListPlantsApiView(APIView):
    """
    get:
    returns list of all plants
    """

    authentication_classes = (TokenAuthentication,)

    def get(self, request):
        try:
            instances = Plants.objects.all().exclude(isDeleted=True)
            serialized = PlantsSerializer(instances, many=True).data
            return response(
                status_code=stat_code.HTTP_200_OK,
                status=True,
                msg="Retreived list of plants.",
                data=serialized,
            )
        except Exception as e:
            return response(status_code=stat_code.HTTP_403_FORBIDDEN, status=False, msg=str(e))


class UpdateDeletePlantsApiView(APIView):
    """
    put:
    update data of a specific plant

    delete:
    delete a specific plant
    """

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsNurseryUser,)

    def put(self, request, plant_id):
        try:
            if "owner" in request.data:
                del request.data["owner"]
            plant_instance = Plants.objects.exclude(isDeleted=True).get(id=plant_id, owner_id=request.user.id)
            serializer_class = PlantsSerializer(plant_instance, request.data, partial=True)  # accepts partial update
            if serializer_class.is_valid(raise_exception=True):
                serializer_class.save()
                data = serializer_class.data
                return response(status_code=stat_code.HTTP_200_OK, status=True, msg="Updated successfully.", data=data)
            return response(status_code=stat_code.HTTP_403_FORBIDDEN, status=False, msg=serializer_class.errors)
        except Plants.DoesNotExist as ude:
            return response(status_code=stat_code.HTTP_403_FORBIDDEN, status=False, msg="Plant does not exist.")
        except Exception as e:
            return response(status_code=stat_code.HTTP_403_FORBIDDEN, status=False, msg=str(e))

    def delete(self, request, plant_id):
        try:
            plant_instance = Plants.objects.filter(id=plant_id, owner_id=request.user.id).update(isDeleted=True)
            return response(status_code=stat_code.HTTP_200_OK, status=True, msg="Deletion successfuly.")
        except Plants.DoesNotExist as ude:
            return response(status_code=stat_code.HTTP_403_FORBIDDEN, status=False, msg="Plant does not exist.")
        except Exception as e:
            return response(status_code=stat_code.HTTP_403_FORBIDDEN, status=False, msg=str(e))
