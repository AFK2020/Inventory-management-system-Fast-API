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

    class Meta:
        model = Cart
        fields = ("user", "items")
