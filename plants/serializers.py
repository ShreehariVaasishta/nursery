from rest_framework import serializers
from .models import Plants, Cart, Order

# Serializers
class PlantsSerializer(serializers.ModelSerializer):
    get_image_path = serializers.ReadOnlyField()

    class Meta:
        model = Plants
        fields = (
            "id",
            "name",
            "owner",
            "get_image_path",
            "plant_description",
            "price",
            "inStock",
            "isDeleted",
        )


class PlantsUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plants
        fields = (
            "name",
            "plant_images",
            "plant_description",
            "price",
            "inStock",
        )


class PlantCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = (
            "id",
            "user",
            "plant",
            "quantity",
            "total",
            "created_at",
        )


class PlantOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = (
            "id",
            "buyer",
            "plant",
            "quantity",
            "total",
            "is_payed",
            "order_status",
            "ordered_at",
        )
