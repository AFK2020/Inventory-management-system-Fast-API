from django.contrib import admin

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
    Category
)


class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name", "price"
    )
    list_filter = ["category"]



class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "user", "total_amount", "order_status"
    )
    list_filter = ["order_status"]



admin.site.register(Profile)
admin.site.register(Payment)
admin.site.register(Order,OrderAdmin)
admin.site.register(OrderItem)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(ShippingAddress)
admin.site.register(Coupon)
admin.site.register(Category)
admin.site.register(Product, ProductAdmin)
admin.site.register(ProductVariant)
admin.site.register(Wishlist)
admin.site.register(Review)
admin.site.register(CustomUser)
