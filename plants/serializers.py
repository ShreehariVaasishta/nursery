from rest_framework import serializers
from .models import Plants

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