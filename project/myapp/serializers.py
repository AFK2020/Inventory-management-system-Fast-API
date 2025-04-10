from rest_framework import serializers
from myapp.models import (
    CustomUser,
    Profile,
    Payment,
    Order,
    OrderItem,
    Cart,
    CartItem,
    ShippingAddress,
    Coupon,
    Wishlist,
    Review,
    Product,
    ProductVariant,
    Category,
)
from rest_framework import status
from rest_framework.response import Response
from myapp.enum import PaymentMethod, PaymentStatus


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ("email",)


class UserRegisterSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(
        style={"input_type": "password"}, write_only=True, required=True
    )
    contact_number = serializers.CharField()

    class Meta:
        model = CustomUser
        fields = [
            "email",
            "first_name",
            "last_name",
            "password",
            "confirm_password",
            "contact_number",
        ]
        extra_kwargs = {
            "password": {"write_only": True},
        }

    def validate(self, data):
        email = data.get("email")
        if CustomUser.objects.filter(email=email).exists():
            raise serializers.ValidationError("User email already exists.")

        password = data.get("password")
        confirm_password = data.get("confirm_password")

        if password != confirm_password:
            raise serializers.ValidationError({"Error": "Passwords must match."})

        return data

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            email=validated_data["email"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
            password=validated_data["password"],
        )
        Profile.objects.create(
            user=user,
            contact_number=validated_data["contact_number"],
        )
        return validated_data


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = (
            "user",
            "contact_number",
        )

    def update(self, instance, validated_data):
        if "user" in validated_data:
            instance.user = validated_data["user"]

        instance.contact_number = validated_data["contact_number"]
        instance.save()
        return instance


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ("name", "slug", "parent")


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ("name", "category", "price")

    def create(self, validated_data):
        product = Product.objects.create(
            name=validated_data["name"],
            category=validated_data["category"],
            price=validated_data["price"],
        )
        return product


class ProductVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariant
        fields = ("product", "variant_name", "variant_value", "price")


class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ("product_variant", "quantity", "price_at_time")


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(
        source="cartitem_set", many=True
    )  # Use reverse relation to CartItem
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Cart
        fields = ("user", "items")

    def validate(self, data):
        cart_items = data.get("cartitem_set")
        
        for cart_item in cart_items:
            product_variant_id = cart_item["product_variant"]

            try:
                product_variant_obj = ProductVariant.objects.get(
                    id=product_variant_id.id
                )
            except product_variant_obj.DoesNotExist:
                return Response(
                    {"detail": "Product variant not found."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        
        return data

    def update(self, instance, validated_data):

        cart_items = validated_data.get("cartitem_set")
        for cart_item in cart_items:
            product_variant_id = cart_item["product_variant"]
            print("cart_item",cart_item)

            product_variant_obj = ProductVariant.objects.get(id=product_variant_id.id)

            try:
                item = CartItem.objects.get(
                    cart=instance, product_variant=cart_item["product_variant"]
                )
                item.quantity += cart_item["quantity"]
                item.save()

            except:
                CartItem.objects.create(
                    cart=instance,
                    product_variant=cart_item["product_variant"],
                    quantity=cart_item["quantity"],
                    price_at_time=product_variant_obj.price,
                )

        return instance



class PaymentSerializer(serializers.ModelSerializer):


    class Meta:
        model = Payment
        fields = ("order", "payment_method", "payment_status")

    def validate(self, data):
        order_id = data.get('order')
        payment_method = data.get('payment_method')
        payment_status = data.get('payment_status')

        try:
            Order.objects.get(id = order_id.id)
        
        except:
            return Response(
                    {"detail": "Object not found."},
                    status=status.HTTP_400_BAD_REQUEST)
        
        if payment_method not in (method.value for method in PaymentMethod):
            raise serializers.ValidationError(
                {"Invalid Method": "PaymentMethod must be from the specified Methods"},
                status=status.HTTP_400_BAD_REQUEST
            )
        if payment_status not in (pstatus.value for pstatus in PaymentStatus):
            raise serializers.ValidationError(
                {"Invalid Status": "PaymentMethod must be from the specified Methods"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return data
    
    def create(self, validated_data):

        order = Order.objects.get(id = validated_data["order"].id)
        amount = order.total_amount

        payment = Payment.objects.create(
            order = validated_data['order'],
            payment_method = validated_data['payment_method'],
            payment_status = validated_data['payment_status'],
            amount= amount
        )
        return payment
    

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingAddress
        fields =(
        "user",
        "address_line1",
        "address_line2",
        "city",
        "state",
        "postal_code",
        "country",
        "phone_number",
        )
  


class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = (
        "code",
        "discount_amount",
        "is_active",
        "expiration_date"
        )
        read_only_fields =("discount_amount",
        "is_active",
        "expiration_date")


       


