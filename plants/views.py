from django.shortcuts import get_object_or_404
from rest_framework import status as stat_code
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from common_utils.custom_auth import TokenAuthentication, generate_token
from common_utils.permissions import IsNurseryUser, IsBuyerUser
from common_utils.response import response

from .models import Plants, Cart, Order
from .serializers import PlantsSerializer, PlantCartSerializer, PlantOrderSerializer, PlantsUpdateSerializer

# Create your views here.
class PostListPlantsApiView(APIView):
    """
    post:
    Use nursery user token.
    post new plants
    {
        "name": "plant name",
        "plant_description": "lorem ipsum",
        "price": 250 (upto to 2 decimals),
        "inStock": true (bool)
    }

    get:
    Use nursery user token.
    returns list of plants posted by the requesting user
    """

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsNurseryUser,)

    def post(self, request):
        try:
            if "plant_images" not in request.data:
                request.data["plant_images"] = None
            instances = Plants.objects.create(
                name=request.data["name"],
                owner_id=request.user.id,
                plant_images=request.data["plant_images"],
                plant_description=request.data["plant_description"],
                price=request.data["price"],
                inStock=request.data["inStock"],
            )
            return response(
                status_code=stat_code.HTTP_200_OK,
                status=True,
                msg="Plant posted successfully.",
            )
        except Exception as e:
            return response(status_code=stat_code.HTTP_403_FORBIDDEN, status=False, msg=str(e))

    def get(self, request):
        try:
            instance = Plants.objects.filter(owner_id=request.user.id).select_related("owner").exclude(isDeleted=True)
            vals = []
            for i in instance.iterator():
                try:
                    img_url = i.plant_images.url
                except Exception as e:
                    img_url = None
                _parse = {
                    "id": i.id,
                    "name": i.name,
                    "owner_id": i.owner_id,
                    "owner_name": i.owner.name,
                    "owner_email": i.owner.email,
                    "plant_images": img_url,
                    "plant_description": i.plant_description,
                    "price": i.price,
                    "inStock": i.inStock,
                }
                vals.append(_parse)
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
    use nursery/buyer user token.
    returns list of all plants for both buyers and nurseries
    """

    authentication_classes = (TokenAuthentication,)

    def get(self, request):
        try:
            instances = Plants.objects.select_related("owner").all().exclude(isDeleted=True)
            vals = []
            for i in instances.iterator():
                try:
                    img_url = i.plant_images.url
                except Exception as e:
                    img_url = None
                _parse = {
                    "id": i.id,
                    "name": i.name,
                    "owner_id": i.owner_id,
                    "owner_name": i.owner.name,
                    "owner_email": i.owner.email,
                    "plant_images": img_url,
                    "plant_description": i.plant_description,
                    "price": i.price,
                    "inStock": i.inStock,
                }
                vals.append(_parse)
            return response(
                status_code=stat_code.HTTP_200_OK,
                status=True,
                msg="Retreived list of plants.",
                data=vals,
            )
        except Exception as e:
            return response(status_code=stat_code.HTTP_403_FORBIDDEN, status=False, msg=str(e))


class RetreiveUpdateDeletePlantsApiView(APIView):
    """
    get:
    use nursery user token.
    return data of a particular plant.

    put:
    use nursery user token
    update data of a specific plant
    {
        "name": "Aglaonema",
        "plant_description": "plant_description11111",
        "price": 25.25,
        "inStock": false,
        "isDeleted": false
    }

    delete:
    use nursery user token
    delete a specific plant
    """

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsNurseryUser,)

    def get(self, request, plant_id):
        try:
            plant_instance = Plants.objects.exclude(isDeleted=True).get(id=plant_id, owner_id=request.user.id)
            serialized = PlantsSerializer(plant_instance).data
            return response(
                status_code=stat_code.HTTP_200_OK, status=True, msg="Retreived successfully.", data=serialized
            )
        except Plants.DoesNotExist as ude:
            return response(status_code=stat_code.HTTP_403_FORBIDDEN, status=False, msg="Plant does not exist.")
        except Exception as e:
            return response(status_code=stat_code.HTTP_403_FORBIDDEN, status=False, msg=str(e))

    def put(self, request, plant_id):
        try:
            if "owner" in request.data:
                del request.data["owner"]
            plant_instance = Plants.objects.exclude(isDeleted=True).get(id=plant_id, owner_id=request.user.id)
            serializer_class = PlantsUpdateSerializer(
                plant_instance, request.data, partial=True
            )  # accepts partial update
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
    use buyer user token

    get:
    receive cart of a buyer
    use buyer user token
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
                    return response(status_code=stat_code.HTTP_200_OK, status=True, msg="Updated Cart.")
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
            cart_values = (
                Cart.objects.filter(user_id=request.user.id)
                .select_related("buyer", "plant")
                .values(
                    "id",
                    "plant_id",
                    "plant__name",
                    "plant__owner_id",
                    "plant__owner__name",
                    "plant__owner__email",
                    "total",
                    "created_at",
                )
            )
            return response(status_code=stat_code.HTTP_200_OK, status=True, msg="Retreived Cart.", data=cart_values)
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
    use buyer user token
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
    use buyer user token

    get:
    list of all orders placed
    use buyer user token
    """

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsBuyerUser,)

    def post(self, request):
        try:
            place_order = Order.objects.create(
                plant_id=request.data["plant_id"], buyer_id=request.user.id, quantity=request.data["quantity"]
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
    use nursery user token
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
    use nursery user token
    {
        "order_status": "PENDING"
    }
    CHOICES :
        DELIVERED,
        CANCELLED,
        ON_THE_WAY
        PENDING,
        CONFIRMED,
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
            if order_instance.plant.owner.id != request.user.id:
                return response(status_code=stat_code.HTTP_403_FORBIDDEN, status=False, msg="Invalid order id")
            serializer_class = PlantOrderSerializer(order_instance, _ord_stat, partial=True)
            if serializer_class.is_valid(raise_exception=True):
                serializer_class.save()
                serialized = serializer_class.data
                return response(
                    status_code=stat_code.HTTP_200_OK, status=True, msg="Retreived order details.", data=serialized
                )
            return response(status_code=stat_code.HTTP_403_FORBIDDEN, status=False, msg=serializer_class.errors)
        except Order.DoesNotExist as ode:
            return response(
                status_code=stat_code.HTTP_403_FORBIDDEN, status=False, msg="Order with this id does not exist."
            )
        except Exception as e:
            return response(status_code=stat_code.HTTP_403_FORBIDDEN, status=False, msg=str(e))
