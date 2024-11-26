from rest_framework import serializers
from .models import Order, OrderItem
from products.serializers import ProductSerializer


class OrderItemSerializer(serializers.ModelSerializer):
    product_details = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ['id', 'order', 'product', 'product_details', 'quantity']


    def get_product_details(self, obj):
        return ProductSerializer(obj.product).data

class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True, read_only=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'order_items', 'total_price', 'status', 'created_at']
        read_only_fields = ['user', 'total_price', 'created_at', 'status']

    def create(self, validated_data):
        user = self.context['request'].user
        cart_items = user.cart_set.all()

        if not cart_items.exists():
            raise serializers.ValidationError("Your cart is empty.")

        order = Order.objects.create(user=user, total_price=0)

        total_price = 0
        for cart_item in cart_items:
            if cart_item.quantity > cart_item.product.stock:
                raise serializers.ValidationError(f"not enough stock for {cart_item.product.name}")

            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity

            )

            cart_item.product.stock -= cart_item.quantity
            cart_item.product.save()
            total_price += cart_item.quantity * cart_item.product.price

        order.total_price = total_price
        order.save()

        cart_items.delete()

        return order
