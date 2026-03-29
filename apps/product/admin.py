from django.contrib import admin
from modeltranslation.admin import TranslationAdmin, TranslationTabularInline, TranslationStackedInline

from apps.product.models import (
    Category,
    Tag,
    Product,
    ProductImage,
    # Trade,
    Wishlist,
    Like,
    Rank,
    Comment,
    CommentImage,
)
from django.utils.safestring import mark_safe
from decimal import Decimal


@admin.register(Category)
class CategoryAdmin(TranslationAdmin):
    list_display = ('id', 'parent', 'name', 'created_date')
    date_hierarchy = 'created_date'
    search_fields = ('name',)


# @admin.register(Tag)
# class TagAdmin(admin.ModelAdmin):
#     list_display = ('id', 'name')
#     search_fields = ('name',)


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 0
    fields = ('image', 'preview')  # Rasm maydoni va preview
    readonly_fields = ('preview',)  # Preview faqat o‘qish uchun

    def preview(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="100" height="100" />')
        return "-"

    preview.short_description = "Image Preview"


@admin.register(Product)
class ProductAdmin(TranslationAdmin):
    inlines = (ProductImageInline,)
    list_display = (
        'name', 'price', 'quantity', 'worth', 'format_discount', 'discounted_price', 'category', 'created_date')
    fields = [
        'name', 'category', 'price', 'discount', 'description', 'quantity', 'worth',
         'modified_date', 'created_date'
    ]
    readonly_fields = (
        'average_rank', 'get_likes_count', 'is_available', 'modified_date', 'created_date')
    date_hierarchy = 'created_date'
    search_fields = ('name', 'category__name')
    list_filter = ('category',)
    autocomplete_fields = ('category',)

    def discounted_price(self, obj):
        if obj.discount:  # Agar chegirma mavjud bo‘lsa
            discounted_amount = obj.price * (Decimal(1) - obj.discount / Decimal(100))  # Decimal ishlatish
            return f"{discounted_amount:.2f}"
        return obj.price  # Agar chegirma bo‘lmasa, oddiy narx qaytariladi
    discounted_price.short_description = "Discounted Price"

    def format_discount(self, obj):
        return f"{obj.discount}%"  # Foiz belgisini qo‘shamiz
    format_discount.short_description = "Discount (%)"  # Admin panelda ustun nomi


# @admin.register(Trade)
# class TradeAdmin(admin.ModelAdmin):
#     list_display = ('id', 'product', 'quantity', 'created_date')
#     date_hierarchy = 'created_date'
#     search_fields = ('product__name',)


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'user')
    search_fields = ('product__name', 'user__name')


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'user')
    search_fields = ('product__name', 'user__name')


@admin.register(Rank)
class RankAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'user', 'rank')
    search_fields = ('product__name', 'user__name')
    list_filter = ('rank',)


@admin.register(CommentImage)
class CommentImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'image')

# @admin.register(Comment)
# class CommentAdmin(admin.ModelAdmin):
#     list_display = ('id', 'product', 'user', 'parent', 'top_level_comment_id', 'created_date')
#     date_hierarchy = 'created_date'
#     search_fields = ('product__name', 'user__name', 'parent__name')
#     readonly_fields = ('top_level_comment_id', 'created_date')
