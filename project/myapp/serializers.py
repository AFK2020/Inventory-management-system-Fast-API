from rest_framework import serializers
from myapp.models import(
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
    Category
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


