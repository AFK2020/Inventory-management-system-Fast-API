from rest_framework import generics, status, viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from .permissions import ModifiedAdminPermission
import django_filters

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

from myapp.serializers import (
    UserRegisterSerializer,
    ProfileSerializer,
    CategorySerializer,
    ProductSerializer,
    ProductVariantSerializer,
    CartSerializer,
    CartItemSerializer,
    PaymentSerializer,
    AddressSerializer,
    CouponSerializer
)


class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserRegisterSerializer
    permission_classes = [AllowAny]


class LogoutView(APIView):
    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(
                {"message": "Logged out successfully"},
                status=status.HTTP_205_RESET_CONTENT,
            )
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class ProfileView(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [ModifiedAdminPermission]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user.id)


class CategoryAPIView(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer



class ProductAPIView(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = [ModifiedAdminPermission]
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]
    filterset_fields = ['name', 'is_active']

    def get_queryset(self):
        categoryname = self.kwargs.get("categoryname", None)

        if categoryname:
            return self.queryset.filter(category=categoryname)

        return self.queryset


class ProductVariantAPIView(viewsets.ModelViewSet):
    queryset = ProductVariant.objects.all()
    serializer_class = ProductVariantSerializer
    permission_classes = [ModifiedAdminPermission]

    def get_queryset(self):
        product = self.kwargs.get("product", None)
        if product:
            return self.queryset.filter(product=product)

        return self.queryset


class CartAPI(viewsets.ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer

    def get_queryset(self):
        user = self.request.user

        return self.queryset.filter(user=user)

    def partial_update(self, request, pk=None):

        cart, _ = Cart.objects.get_or_create(user=self.request.user)
        serializer = CartSerializer(cart, data=request.data, partial=True)
        print(serializer)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["patch"])
    def update_cart_quantity(self, request, pk=None):

        try:
            cart = Cart.objects.get(user=self.request.user)

        except Exception:
            return Response(status=status.HTTP_404_NOT_FOUND)

        try:
            item = CartItem.objects.get(cart=cart, id=pk)
            quantity = request.data["quantity"]
            item.quantity = quantity
            item.save()

        except Exception:
            return Response(
                {"detail": "Item not found in cart"}, status=status.HTTP_404_NOT_FOUND
            )

        return Response({"detail": "Item Quantity Updated"}, status=status.HTTP_200_OK)

    def destroy(self, request, pk=None):
        try:
            cart = Cart.objects.get(user=self.request.user)

        except Exception:
            return Response(status=status.HTTP_404_NOT_FOUND)

        try:
            CartItem.objects.get(cart=cart, id=pk).delete()

        except Exception:
            return Response(
                {"detail": "Item not found in cart"}, status=status.HTTP_404_NOT_FOUND
            )

        return Response(
            {"detail": "Item Successfully deleted"}, status=status.HTTP_200_OK
        )


class PaymentAPIView(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    def create(self, request):
        serializer = PaymentSerializer(data=self.request.data)
        print(serializer)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {"detail": "Payment Successfully processed"}, status=status.HTTP_201_CREATED
        )

    def retrieve(self, request, pk=None):
        try:
            order = Order.objects.get(id=pk)
        except:
            return Response(
                {"detail": "Order not found"}, status=status.HTTP_404_NOT_FOUND
            )
        try:
            payment_info = Payment.objects.get(order=order)
        except:
            return Response(
                {"detail": "Payment info not found"}, status=status.HTTP_404_NOT_FOUND
            )

        return Response(payment_info, status=status.HTTP_200_OK)


class ShippingAddressAPIView(viewsets.ModelViewSet):
    queryset = ShippingAddress.objects.all()
    serializer_class = AddressSerializer

    def retrieve(self, request, pk = None):
        try:
            address = ShippingAddress.objects.filter(user=pk)
        except:
            return Response(
                {"detail": "Address not found"}, status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = AddressSerializer(address, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class CouponAPIView(viewsets.ModelViewSet):
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer

    @action(detail=True,methods=["post"])
    def apply_coupon(self, request, pk=None):

        code = request.data["code"]

        try:
            order = Order.objects.get(id = pk)
            print(order)
        except Exception:
            return Response(
                {"detail": "Order not found"}, status=status.HTTP_404_NOT_FOUND
            )

        try:
            coupon = Coupon.objects.get(code = code)
            print(coupon)
        except Exception:
            return Response(
                {"detail": "Coupon not found"}, status=status.HTTP_404_NOT_FOUND
            )
        
        if not coupon.is_active:
            return Response(
                {"Invalid Status": "Coupon has expired"},
                status=status.HTTP_400_BAD_REQUEST)
        
        discount = coupon.discount_amount
        order.total_amount -= discount 
        order.save()

        return Response(
            {"detail": "Coupon Successfully applied"}, status=status.HTTP_200_OK)