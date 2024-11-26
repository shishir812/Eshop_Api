from rest_framework import serializers
from .models import Cart
from products.models import Product
from products.serializers import ProductSerializer


class CartSerializer(serializers.ModelSerializer):
    product_details = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields =['id', 'user', 'product', 'product_details', 'quantity', 'added_at']
        read_only_fields = ['user', 'added_at']

    def get_product_details(self, obj):
        return ProductSerializer(obj.product).data

    def validate_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError("Quantity must be at least 1.")
        return value

    def create(self, validated_data):
        user = self.context['request'].user
        product = self.validated_data['product']
        quantity = self.validated_data['quantity']

        if quantity > product.stock:
            raise serializers.ValidationError("Not enough stock available")


        cart_item, created = Cart.objects.get_or_create(
            user=user,
            product=product,
            defaults={'quantity': quantity}

        )

        if not created:
            cart_item.quantity += quantity
            if cart_item.quantity > product.stock:
                raise serializers.ValidationError("Not enough stock available.")
            cart_item.save()

        return cart_item

