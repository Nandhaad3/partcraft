from django.contrib import admin
from .models import *

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'parts_brand','parts_category','subcategory_name','parts_price', 'parts_status','parts_offer','main_image']
#
@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['product', 'image']

# admin.site.register(Product)


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ['vehicle_name', 'vehicle_model', 'vehicle_year', 'vehicle_type']

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['brand_name', 'brand_image']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['category_name', 'category_image']


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ['wishlist_name', 'wishlist_product']


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['user','session_key', 'product', 'quantity']
