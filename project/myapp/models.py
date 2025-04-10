from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager,
)
from django.db.models.signals import post_save
from django.dispatch import receiver
from myapp.customfield import CustomPhoneNumberField
from myapp.validators.image_size import validate_image
from myapp.enum import PriceChoice,OrderStatus,TransactionStatus,PaymentMethod,PaymentStatus
# from django.conf import settings


class CustomUserManager(BaseUserManager):
    def _create_user(self, email, password, first_name, last_name, **extra_fields):
        if not email:
            raise ValueError("Email must be provided")
        if not password:
            raise ValueError("Password is not provided")

        user = self.model(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password, first_name, last_name, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, first_name, last_name, **extra_fields)

    def create_superuser(self, email, password, first_name, last_name, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_superuser", True)
        return self._create_user(email, password, first_name, last_name, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(db_index=True, unique=True, max_length=254)
    first_name = models.CharField(max_length=240)
    last_name = models.CharField(max_length=255)
    date_joined = models.DateField(auto_now_add=True)

    is_staff = models.BooleanField(
        default=True
    )  # must needed, otherwise you won't be able to loginto django-admin.
    is_active = models.BooleanField(
        default=True
    )  # must needed, otherwise you won't be able to loginto django-admin.
    is_superuser = models.BooleanField(
        default=False
    )  # this field we inherit from PermissionsMixin.

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    def __str__(self):
        return f"{self.email} : {self.date_joined}"

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"



class Profile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, verbose_name="Name", related_name="profile")
    profile_picture = models.ImageField(
        upload_to="profile_pics/",
        help_text="Max img size 5mb",
        validators=[validate_image],
        blank=True,
        null=True,
    )
    contact_number = CustomPhoneNumberField(blank=True)

    def __str__(self):
        return f"Profile Id :{self.id}"    

class Category(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(default="", null=True)
    description = models.TextField(null=True, blank=True)
    parent = models.ForeignKey('self',null=True,blank=True, on_delete=models.SET_NULL, related_name="children")


    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name_plural = "Categories"


class Product(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(default="", null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    price = models.IntegerField()
    discount_price = models.IntegerField(null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    inventory_count = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateField(auto_now_add=True)
    updates_at = models.DateField(auto_now=True)

    def __str__(self):
        return f"{self.name}"



class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variant_name = models.CharField( max_length=50)
    variant_value = models.CharField(max_length=50,choices=PriceChoice.choices(), verbose_name="Price Range")
    price = models.IntegerField()
    stock_count = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.variant_name} : {self.product.name}"


class Cart(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, verbose_name="User Name", related_name="cart")
    created_at = models.DateField(auto_now_add=True)
    updates_at = models.DateField(auto_now=True)

    def __str__(self):
        return f"{self.user.email}"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart,on_delete=models.CASCADE )
    product_variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price_at_time = models.IntegerField()

    def __str__(self):
        return f"{self.cart.user.email}"



class Order(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, verbose_name="User Name", related_name="order")
    order_status = models.CharField(max_length=50,choices=OrderStatus.choices(), verbose_name="Order Status")
    total_amount = models.IntegerField()
    created_at = models.DateField(auto_now_add=True)
    updates_at = models.DateField(auto_now=True)

    def __str__(self):
        return f"{self.user.email}"



class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="order_item")
    product_variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.IntegerField()

    def __str__(self):
        return f"{self.order.user.email} - {self.product_variant.product.name} "
    


class Payment(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    payment_method = models.CharField(max_length=50, choices=PaymentMethod.choices(), verbose_name="Payment Method")
    amount = models.IntegerField()
    payment_status = models.CharField(max_length=50, choices=PaymentStatus.choices(), verbose_name="Payment Status")


    def __str__(self):
        return f"{self.order.user.email} - {self.amount} "
    
    @property
    def payment_amount(self):
        self.amount = self.order.total_amount
        return self.amount




class ShippingAddress(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="shipping_address")
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)
    phone_number = CustomPhoneNumberField()

    def __str__(self):
        return f"{self.user.email} - {self.address_line1}, {self.city}, {self.state}"
    
    class Meta:
        verbose_name = "Shipping Address"
        verbose_name_plural = "Shipping Addresses"
    

class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="review")
    rating = models.IntegerField()
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Review by {self.user.email} for {self.product.name}"
    

class Wishlist(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE,related_name="wishlist")
    products = models.ManyToManyField(Product)

    def __str__(self):
        return f"Wishlist of {self.user.email}"
    

class Coupon(models.Model):
    code = models.CharField(max_length=20, unique=True)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    expiration_date = models.DateTimeField()

    def __str__(self):
        return f"Coupon {self.code} - {'Active' if self.is_active else 'Inactive'}"
    

