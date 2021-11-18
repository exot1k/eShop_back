from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline

from .models import *


class ImageGalleryInline(GenericTabularInline):
    model = ImageGallery
    readonly_fields = ('image_url',)


@admin.register(Shoes)
class ShoesAdmin(admin.ModelAdmin):
    inlines = [ImageGalleryInline]


@admin.register(ShoesBrand)
class ShoesBrandAdmin(admin.ModelAdmin):
    inlines = [ImageGalleryInline]


admin.site.register([User, ShoesType, ImageGallery, Cart, CartProduct, Order, Customer])
