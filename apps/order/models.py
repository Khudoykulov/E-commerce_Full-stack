from email.policy import default
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models.signals import pre_save
from apps.account.models import User, UserLocation
from apps.product.models import Product
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.auth.models import Group
from django.utils import timezone
from django.http import HttpResponse
from apps.order.utils import generate_receipt_pdf  # PDF yaratish funksiyasi


class Promo(models.Model):
    name = models.CharField(max_length=8)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='promos')
    description = models.TextField(null=True, blank=True)
    discount = models.PositiveIntegerField(validators=[MaxValueValidator(100)])
    min_price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(100.00)])
    members = models.ManyToManyField(User, blank=True)
    expire_date = models.DateField(null=True, blank=True)
    is_expired = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class CartItem(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, related_name='cart_items')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField(default=1)
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.product.name if self.product else "order_items"

    @property
    def get_amount(self):
        return (float(self.product.price) * ((100 - (self.product.discount or 0)) / 100)) * self.quantity


from django.core.exceptions import ValidationError
import mimetypes


def validate_file_type(value):
    allowed_mime_types = [
        "image/",  # Barcha rasm formatlari (JPEG, PNG, GIF, WEBP, SVG, TIFF, BMP va boshqalar)
        "application/pdf",  # PDF fayllar
        "application/msword",  # .doc
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",  # .docx
        "application/vnd.ms-excel",  # .xls
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",  # .xlsx
        "application/zip",  # ZIP fayllar
        "application/x-rar-compressed",  # RAR fayllar
        "application/x-7z-compressed",  # 7z fayllar
    ]

    mime_type, _ = mimetypes.guess_type(value.name)

    if not mime_type:
        raise ValidationError("Noto‘g‘ri fayl turi!")

    # Barcha rasm formatlarini avtomatik qabul qilish uchun "image/" bilan boshlanganlarini tekshiramiz
    if not any(mime_type.startswith(allowed) for allowed in allowed_mime_types):
        raise ValidationError("Faqat rasm yoki hujjat fayllarini yuklash mumkin!")


class Courier(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15)

    # Group tanlanadigan qilib ManyToOne (ya'ni ForeignKey)
    group = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.user}  --->  {self.phone}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.user:
            self.user.is_staff = True
            self.user.is_active = True
            self.user.save()

            # Avvalgi guruhlardan tozalaymiz (agar xohlasangiz)
            self.user.groups.clear()

            # Tanlangan groupga biriktiramiz
            if self.group:
                self.user.groups.add(self.group)


class Order(models.Model):
    STATUS_CHOICES = [
        ('preparing', 'Tayyorlanmoqda'),
        ('out_for_delivery', 'Yetkazilmoqda'),
        ('delivered', 'Yetkazildi'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    location = models.ForeignKey(UserLocation, on_delete=models.SET_NULL, null=True, blank=True,related_name='orders_location')
    location_data = models.JSONField(encoder=DjangoJSONEncoder, null=True, blank=True)
    items = models.ManyToManyField(CartItem)
    items_data = models.JSONField(encoder=DjangoJSONEncoder, null=True, blank=True)
    file = models.FileField(blank=True, null=True, upload_to="uploads/", validators=[validate_file_type])
    promo = models.CharField(max_length=8, null=True, blank=True)
    courier = models.ForeignKey(Courier, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='preparing')
    payment_confirmed = models.BooleanField(default=None, null=True, blank=True,)  # Yangi maydon
    assigned_date = models.DateTimeField(null=True, blank=True)
    delivered_date = models.DateTimeField(null=True, blank=True)
    modified_date = models.DateTimeField(auto_now_add=True)
    created_date = models.DateTimeField(auto_now_add=True)

    @property
    def get_amount(self):
        total = 0.0
        if self.items_data and isinstance(self.items_data, list):
            total = sum(float(item.get('price', 0)) for item in self.items_data)
        elif self.items.exists():
            total = sum(item.get_amount for item in self.items.all())

        if self.promo:
            try:
                promo_object = Promo.objects.get(name=self.promo)
                return float(total * ((100 - promo_object.discount or 0) / 100))
            except Promo.DoesNotExist:
                return round(total, 2)
        return round(total, 2)

    def generate_pdf_receipt(self):
        if self.status == 'delivered':
            order_data = {
                'user': self.user.name,
                'order_date': self.created_date.strftime("%Y-%m-%d %H:%M"),
                'amount': str(self.get_amount),
                'items': self.items_data or [  # items_data dan foydalanamiz, agar bo'sh bo'lsa items dan olish mumkin
                    {
                        'product_id': item.product.id,
                        'name': item.product.name,
                        'product_image': item.product.images.first().image.url if item.product.images.exists() else None,
                        # Birinchi rasm
                        'quantity': item.quantity,
                        'price': str(item.get_amount)
                    } for item in self.items.all()
                ]
            }
            pdf_content = generate_receipt_pdf(order_data)
            response = HttpResponse(pdf_content, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="order_{self.id}_receipt.pdf"'
            return response
        else:
            return None

    def save(self, *args, **kwargs):
        if self.location and not self.location_data:
            self.location_data = {
                "id": self.location.id,
                "location": self.location.location,
                "latitude": self.location.latitude,
                "longitude": self.location.longitude,
                "floor": self.location.floor,
                "apartment": self.location.apartment,
                "modified_date": self.location.modified_date,
                "created_date": self.location.created_date,
            }
        if self.courier and not self.assigned_date:
            self.assigned_date = timezone.now()
            if self.status != 'out_for_delivery':
                self.status = 'out_for_delivery'
        if self.status == 'delivered' and not self.delivered_date:
            self.delivered_date = timezone.now()
        super().save(*args, **kwargs)
