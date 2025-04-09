from rest_framework import generics, status, viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from .permissions import ModifiedAdminPermission

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

from myapp.serializers import (
    UserRegisterSerializer,
    ProfileSerializer,
    CategorySerializer,
    ProductSerializer,
    ProductVariantSerializer,
    CartSerializer,
    CartItemSerializer
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

    def get_queryset(self):
        categoryname = self.kwargs.get('categoryname', None)  

        if categoryname:
            return self.queryset.filter(category = categoryname)
        
        return self.queryset
        

class ProductVariantAPIView(viewsets.ModelViewSet):
    queryset = ProductVariant.objects.all()
    serializer_class = ProductVariantSerializer
    permission_classes = [ModifiedAdminPermission]

    def get_queryset(self):
        product = self.kwargs.get('product', None)  
        if product:
            return self.queryset.filter(product = product)
        
        return self.queryset
        


class CartAPI(viewsets.ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer


    def get_queryset(self):
        user = self.request.user

        return self.queryset.filter(user=user)
    

    @action(detail=False, methods=['POST'], url_path='add')
    def add_to_cart(self, request):
        """
        Add an item to the cart.
        """
        user = request.user
        cart, created = Cart.objects.get_or_create(user=user)

        product_variant_id = request.data.get('product_variant')
        quantity = request.data.get('quantity')

        try:
            product_variant = ProductVariant.objects.get(id=product_variant_id)
        except ProductVariant.DoesNotExist:
            return Response({'detail': 'Product variant not found.'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if the item already exists in the cart
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart, product_variant=product_variant,
            defaults={'quantity': quantity, 'price_at_time': product_variant.price}
        )

        if not created:  # If the item already exists, just update the quantity
            cart_item.quantity += quantity
            cart_item.save()

        return Response(CartItemSerializer(cart_item).data, status=status.HTTP_201_CREATED)
