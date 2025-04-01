from rest_framework import serializers
from .models import Product

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "name", "description", "category", "image", "price", "stock", "created_at"]
        read_only_fields = ["created_at"]