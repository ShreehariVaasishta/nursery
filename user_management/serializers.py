from rest_framework import serializers
from .models import Buyer, Nursery

# Serializers

# Buyer Serializers
class BuyerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Buyer
        fields = (
            "email",
            "first_name",
            "middle_name",
            "last_name",
            "created_at",
            "isdeleted",
        )


class NurserySerializer(serializers.ModelSerializer):
    class Meta:
        model = Nursery
        fields = (
            "email",
            "name",
            "about",
            "ratings",
            "created_at",
        )