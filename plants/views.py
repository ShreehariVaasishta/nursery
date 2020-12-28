from django.shortcuts import get_object_or_404
from rest_framework import status as stat_code
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from common_utils.custom_auth import TokenAuthentication, generate_token
from common_utils.permissions import IsNurseryUser, IsBuyerUser
from common_utils.response import response

from .models import Plants, Cart, Order
from .serializers import PlantsSerializer, PlantCartSerializer, PlantOrderSerializer

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
            vals = (
                Plants.objects.filter(owner_id=request.user.id)
                .select_related("owner")
                .exclude(isDeleted=True)
                .values(
                    "id",
                    "name",
                    "owner_id",
                    "owner__name",
                    "owner__email",
                    "image",
                    "plant_description",
                    "price",
                    "inStock",
                )
            )
            return response(
                status_code=stat_code.HTTP_200_OK,
                status=True,
                msg="Retreived list of plants.",
                data=vals,
            )
        except Exception as e:
            return response(status_code=stat_code.HTTP_403_FORBIDDEN, status=False, msg=str(e))


class ListPlantsApiView(APIView):
    """
    get:
    returns list of all plants for both buyers and nurseries
    """

    authentication_classes = (TokenAuthentication,)

    def get(self, request):
        try:
            instances = (
                Plants.objects.all()
                .select_related("owner")
                .exclude(isDeleted=True)
                .values(
                    "id",
                    "name",
                    "owner_id",
                    "owner__name",
                    "owner__email",
                    "image",
                    "plant_description",
                    "price",
                    "inStock",
                )
            )
            return response(
                status_code=stat_code.HTTP_200_OK,
                status=True,
                msg="Retreived list of plants.",
                data=instances,
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


class AddGetCartApiView(APIView):
    """
    post:
    add to cart
    if exists, quantity is updated

    get:
    receive cart of a specific buyer
    """

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsBuyerUser,)

    def post(self, request):
        try:
            try:
                cart_instance = Cart.objects.get(plant_id=request.data["plant_id"], user_id=request.user.id)
                quantity = request.data["quantity"]
                request.data.clear()
                request.data["quantity"] = quantity
                serializer_class = PlantCartSerializer(
                    cart_instance, request.data, partial=True
                )  # accepts partial update
                if serializer_class.is_valid(raise_exception=True):
                    serializer_class.save()
                    serialized = serializer_class.data
                    return response(
                        status_code=stat_code.HTTP_200_OK, status=True, msg="Updated Cart.", data=serialized
                    )
                return response(status_code=stat_code.HTTP_403_FORBIDDEN, status=False, msg=serializer_class.errors)
            except Cart.DoesNotExist as cde:
                add_to_cart = Cart.objects.create(
                    plant_id=request.data["plant_id"], user_id=request.user.id, quantity=request.data["quantity"]
                )
                serialized = PlantCartSerializer(add_to_cart).data
                return response(status_code=stat_code.HTTP_200_OK, status=True, msg="Added to Cart.", data=serialized)
        except Plants.DoesNotExist as ude:
            return response(status_code=stat_code.HTTP_403_FORBIDDEN, status=False, msg="Plant does not exist.")
        except Exception as e:
            return response(status_code=stat_code.HTTP_403_FORBIDDEN, status=False, msg=str(e))

    def get(self, request):
        try:
            cart_instance = Cart.objects.filter(user_id=request.user.id)
            serialized = PlantCartSerializer(cart_instance, many=True).data
            return response(status_code=stat_code.HTTP_200_OK, status=True, msg="Retreived Cart.", data=serialized)
        except Cart.DoesNotExist as cde:
            return response(
                status_code=stat_code.HTTP_403_FORBIDDEN,
                status=False,
                msg="Failed to retreive few products from your cart.",
            )
        except Exception as e:
            return response(status_code=stat_code.HTTP_403_FORBIDDEN, status=False, msg=str(e))


class DeleteCartApiView(APIView):
    """
    delete:
    delete a item from cart
    """

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsBuyerUser,)

    def delete(self, request, cart_id):
        try:
            cart_instance = Cart.objects.filter(id=cart_id, user_id=request.user.id).delete()
            return response(status_code=stat_code.HTTP_200_OK, status=True, msg="Removed from Cart.")
        except Cart.DoesNotExist as cde:
            return response(
                status_code=stat_code.HTTP_403_FORBIDDEN,
                status=False,
                msg="There's no cart item.",
            )
        except Exception as e:
            return response(status_code=stat_code.HTTP_403_FORBIDDEN, status=False, msg=str(e))


class AddGetOrderApiView(APIView):
    """
    post:
    place an order

    get:
    list of all orders placed
    """

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsBuyerUser,)

    def post(self, request):
        try:
            place_order = Order.objects.create(
                plant_id=request.data["plant_id"], user_id=request.user.id, quantity=request.data["quantity"]
            )
            return response(status_code=stat_code.HTTP_200_OK, status=True, msg="New Order Placed successfully.")
        except Plants.DoesNotExist as cde:
            return response(
                status_code=stat_code.HTTP_403_FORBIDDEN,
                status=False,
                msg="Plant does not exist.",
            )
        except Exception as e:
            return response(status_code=stat_code.HTTP_403_FORBIDDEN, status=False, msg=str(e))

    def get(self, request):
        try:
            order_vals = (
                Order.objects.filter(buyer_id=request.user.id)
                .select_related("buyer", "plant")
                .values(
                    "id",
                    "buyer_id",
                    "buyer__first_name",
                    "buyer__email",
                    "plant_id",
                    "plant__name",
                    "plant__owner_id",
                    "plant__owner__name",
                    "plant__owner__email",
                    "total",
                    "is_payed",
                    "order_status",
                    "ordered_at",
                )
            )
            return response(
                status_code=stat_code.HTTP_200_OK, status=True, msg="Retreived order list(s).", data=order_vals
            )
        except Exception as e:
            return response(status_code=stat_code.HTTP_403_FORBIDDEN, status=False, msg=str(e))


class NurseryViewOrdersApiView(APIView):
    """
    get:
    list of all orders placed
    """

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsNurseryUser,)

    def get(self, request):
        try:
            order_vals = (
                Order.objects.filter(plant__owner_id=request.user.id)
                .select_related("plant", "buyer")
                .order_by("-ordered_at")
                .values(
                    "id",
                    "buyer_id",
                    "buyer__first_name",
                    "buyer__email",
                    "plant_id",
                    "plant__name",
                    "plant__owner_id",
                    "plant__owner__name",
                    "plant__owner__email",
                    "total",
                    "is_payed",
                    "order_status",
                    "ordered_at",
                )
            )
            return response(
                status_code=stat_code.HTTP_200_OK, status=True, msg="Retreived order list(s).", data=order_vals
            )
        except Exception as e:
            return response(status_code=stat_code.HTTP_403_FORBIDDEN, status=False, msg=str(e))


class UpdateOrderStatusApiView(APIView):
    """
    put:
    update
    """

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsNurseryUser,)

    def put(self, request, order_id):
        try:
            _ord_stat = {}
            if "order_status" in request.data:
                _ord_stat["order_status"] = request.data["order_status"]
            if "is_payed" in request.data:
                _ord_stat["is_payed"] = request.data["is_payed"]
            order_instance = Order.objects.get(pk=order_id)
            serializer_class = PlantOrderSerializer(order_instance, _ord_stat, partial=True)
            if serializer_class.is_valid(raise_exception=True):
                serializer_class.save()
                serialized = serializer_class.data
                return response(
                    status_code=stat_code.HTTP_200_OK, status=True, msg="Retreived order list(s).", data=serialized
                )
            return response(status_code=stat_code.HTTP_403_FORBIDDEN, status=False, msg=serializer_class.errors)
        except Order.DoesNotExist as ode:
            return response(
                status_code=stat_code.HTTP_403_FORBIDDEN, status=False, msg="Order with this id does not exist."
            )
        except Exception as e:
            return response(status_code=stat_code.HTTP_403_FORBIDDEN, status=False, msg=str(e))
