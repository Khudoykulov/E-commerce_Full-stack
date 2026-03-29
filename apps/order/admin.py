from django.contrib import admin
from django.utils.html import format_html
from django.core.exceptions import ValidationError
from .models import CartItem, Order, Promo, Courier
from django.urls import path, reverse
from django.http import HttpResponse
from django.db import transaction
from django.utils.safestring import mark_safe
import json
from django.contrib.admin.widgets import AdminRadioSelect
from django.db import models  # Bu qatorni qo'shing


@admin.register(Promo)
class PromoAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'name', 'discount', 'min_price', 'expire_date', 'is_expired', 'created_date')
    date_hierarchy = 'created_date'
    list_filter = ('is_expired',)
    filter_horizontal = ('members',)
    readonly_fields = ('created_date',)
    search_fields = ('user__phone', 'user__name')


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'product', 'quantity', 'get_amount', 'created_date')
    search_fields = ('product__name', 'user__phone', 'user__name')
    date_hierarchy = 'created_date'
    readonly_fields = ('created_date',)


@admin.register(Courier)
class CourierAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'group')
    search_fields = ('user__name', 'user__phone', 'phone', 'group__name')
    list_filter = ('group',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'get_user_name', 'get_user_phone', 'status', 'payment_confirmed', 'courier', 'get_file_link',
        'get_amount', 'location_address',
        'created_date')
    list_display_links = ('id', 'get_user_name', 'get_amount',)
    fields = ['get_user_name', 'get_user_phone', 'formatted_items_data', 'get_amount', 'status',
              'payment_confirmed',
              'courier',
              'created_date', 'formatted_location_data']
    date_hierarchy = 'created_date'
    readonly_fields = ('get_amount', 'formatted_items', 'formatted_items_data', 'get_user_name', 'get_user_phone',
                       'assigned_date',
                       'delivered_date', 'created_date', 'modified_date', 'formatted_location_data')

    formfield_overrides = {
        models.BooleanField: {'widget': AdminRadioSelect(choices=((True, 'Tastiqlash'), (False, 'Rad etish')))},
    }

    def payment_confirmed(self, obj):
        return "Tulov holati"

    payment_confirmed.short_description = "Tulov holati"  # O'zgartirildi

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_staff and not request.user.groups.filter(name='Courier').exists():
            return qs
        elif request.user.groups.filter(name='Courier').exists():
            try:
                courier = Courier.objects.get(user=request.user)
                return qs.filter(courier=courier)
            except Courier.DoesNotExist:
                return qs.none()
        else:
            return qs.none()

    def has_change_permission(self, request, obj=None):
        if request.user.is_staff and not request.user.groups.filter(name='Courier').exists():
            return True
        elif request.user.groups.filter(name='Courier').exists():
            if obj and obj.courier and obj.courier.user == request.user:
                return True
            return False
        return False

    def get_readonly_fields(self, request, obj=None):
        if request.user.groups.filter(name='Courier').exists():
            all_fields = [f.name for f in self.model._meta.fields] + [f.name for f in self.model._meta.many_to_many]
            return [f for f in all_fields if f != 'status']
        else:
            return self.readonly_fields

    def formatted_location_data(self, obj):
        if obj.location_data:
            formatted_json = json.dumps(obj.location_data, indent=4, ensure_ascii=False)
            return mark_safe(f"""
            <style>
                pre {{
                    background-color: #282C34;
                    color: #61DAFB;
                    padding: 10px;
                    border-radius: 5px;
                    font-size: 18px;
                    overflow-x: auto;
                }}
            </style>
            <pre>{formatted_json}</pre>
            """)
        return "N/A"

    formatted_location_data.short_description = "Joylashuv Ma'lumotlari"

    def location_address(self, obj):
        if obj.location_data:
            return obj.location_data.get('location', 'N/A')
        return "N/A"

    location_address.short_description = "Manzil"

    def get_file_link(self, obj):
        if obj.file:
            return format_html('<a href="{}" download>{}</a>', obj.file.url, "Faylni Yuklab Olish 📂")
        return "Fayl Yo'q"

    get_file_link.short_description = "Fayl"

    def get_user_name(self, obj):
        return obj.user.name

    get_user_name.short_description = "Foydalanuvchi Ismi"

    def get_user_phone(self, obj):
        return obj.user.phone

    get_user_phone.short_description = "Foydalanuvchi Telefon Raqami"

    def formatted_items(self, obj):
        if obj.items.exists():
            items_html = "<ul>"
            for item in obj.items.all():
                items_html += f"<li>{item.product.name} - {item.quantity} dona</li>"
            items_html += "</ul>"
            return format_html(items_html)
        return "Mahsulotlar Yo'q"

    formatted_items.short_description = "Mahsulotlar"

    def formatted_items_data(self, obj):
        if obj.items_data:
            formatted_json = json.dumps(obj.items_data, indent=4, ensure_ascii=False)
            return mark_safe(f"""
            <style>
                pre {{
                    background-color: #282C34;
                    color: #61DAFB;
                    padding: 10px;
                    border-radius: 5px;
                    font-size: 18px;
                    overflow-x: auto;
                }}
            </style>
            <pre>{formatted_json}</pre>
            """)
        return "N/A"

    formatted_items_data.short_description = "Mahsulotlar Ma'lumotlari"

    def save_model(self, request, obj, form, change):
        with transaction.atomic():
            super().save_model(request, obj, form, change)

    def pdf_receipt_link(self, obj):
        if obj.status == 'delivered':
            url = reverse('admin:order-pdf', args=[obj.id])
            return format_html('<a href="{}">PDFni Yuklab Olish</a>', url)
        return "Mavjud Emas"

    pdf_receipt_link.short_description = 'PDF Chek'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<int:order_id>/pdf/', self.admin_site.admin_view(self.download_pdf), name='order-pdf'),
        ]
        return custom_urls + urls

    def download_pdf(self, request, order_id):
        order = self.get_object(request, order_id)
        if order and order.status == 'delivered':
            pdf_response = order.generate_pdf_receipt()
            if pdf_response:
                return pdf_response
        return HttpResponse("Chek mavjud emas", status=404)
