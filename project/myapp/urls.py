from django.urls import include, path
from rest_framework import routers
from rest_framework_simplejwt.views import (TokenObtainPairView,
                                            TokenRefreshView)

from myapp import views

router = routers.DefaultRouter()
router.register(r'profile', viewset=views.ProfileView, basename='profile')
router.register(r'category', viewset=views.CategoryAPIView, basename='category')
router.register(r'product/category/(?P<categoryname>[^/.]+)', viewset=views.ProductAPIView, basename='product')
router.register(r'product', viewset=views.ProductAPIView, basename='product_all')

router.register(r'productvariant/product/(?P<product>[^/.]+)', viewset=views.ProductVariantAPIView, basename='product_variant')
router.register(r'productvariant', viewset=views.ProductVariantAPIView, basename='product_variant_all')
router.register(r'cart', viewset=views.CartAPI, basename='cart')


urlpatterns = [
    path('', include(router.urls)),
    path('register/', views.UserRegistrationView.as_view()),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', views.LogoutView.as_view(), name='auth_logout'),
]