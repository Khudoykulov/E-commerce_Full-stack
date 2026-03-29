from django.db import models
from django.db.models.signals import pre_save
from random import randint
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError


class UserManager(BaseUserManager):
    def create_user(self, phone, name, password=None, **extra_fields):
        if not phone:
            raise ValueError('The Phone field must be set')
        user = self.model(phone=phone, name=name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, name, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        if not password:
            raise ValueError('Superusers must have a password')
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(phone=phone, name=name, password=password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(max_length=123, )
    phone = models.CharField(max_length=15, unique=True)
    avatar = models.ImageField(null=True, blank=True, upload_to='avatars/')
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    modified_date = models.DateTimeField(auto_now=True)
    created_date = models.DateTimeField(auto_now_add=True)

    objects = UserManager()
    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ['name']

    def clean(self):
        super().clean()
        qs = User.objects.filter(phone=self.phone)
        if self.pk:
            qs = qs.exclude(pk=self.pk)
        if qs.exists():
            raise ValidationError({'phone': "Ushbu telefon raqami allaqachon ro‘yxatdan o‘tgan."})

    def __str__(self):
        return self.name


class UserLocation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='locations')
    location = models.CharField(max_length=255, null=True, blank=True, verbose_name="Manzil")
    latitude = models.CharField(max_length=100, null=True, blank=True, verbose_name="Kenglik")
    longitude = models.CharField(max_length=100, null=True, blank=True, verbose_name="Uzunlik")
    floor = models.CharField(max_length=123, null=True, blank=True, verbose_name="Qavat")
    apartment = models.CharField(max_length=123, null=True, blank=True, verbose_name="Xonadon")
    modified_date = models.DateTimeField(auto_now=True)
    created_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Foydalanuvchi manzili"
        verbose_name_plural = "Foydalanuvchi manzillari"
        ordering = ['-created_date']

    def __str__(self):
        return f"Location of {self.user}: ({self.latitude}, {self.longitude}), ({self.floor}, {self.apartment})"

    def clean(self):
        """Koordinatalarni validatsiya qilish"""
        super().clean()
        if self.latitude:
            try:
                lat = float(self.latitude)
                if not -90 <= lat <= 90:
                    raise ValidationError({'latitude': "Kenglik -90 va 90 orasida bo'lishi kerak"})
            except ValueError:
                raise ValidationError({'latitude': "Kenglik son bo'lishi kerak"})

        if self.longitude:
            try:
                lng = float(self.longitude)
                if not -180 <= lng <= 180:
                    raise ValidationError({'longitude': "Uzunlik -180 va 180 orasida bo'lishi kerak"})
            except ValueError:
                raise ValidationError({'longitude': "Uzunlik son bo'lishi kerak"})

    @property
    def has_coordinates(self):
        """Koordinatalar mavjudligini tekshirish"""
        return bool(self.latitude and self.longitude)

    @property
    def coordinates(self):
        """Koordinatalarni tuple formatda qaytarish"""
        if self.has_coordinates:
            return (float(self.latitude), float(self.longitude))
        return None


class UserToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.PositiveIntegerField()
    is_used = models.BooleanField(default=False)
    created_date = models.DateTimeField(auto_now_add=True)


def user_token_pre_save(sender, instance, *args, **kwargs):
    if not instance.token:
        instance.token = randint(10000, 99999)


pre_save.connect(user_token_pre_save, sender=UserToken)



class NewBlock(models.Model):
    title = models.CharField(max_length=123)
    description = models.TextField(null=True, blank=True)
    image = models.ImageField(null=True, blank=True, upload_to='new_block_image/')
    created_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.title

class Advice(models.Model):
    title = models.CharField(max_length=123)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.title

class Call(models.Model):
    phone = models.CharField(max_length=123, null=True, blank=True)
    telegram = models.CharField(max_length=123, null=True, blank=True)
    instagram = models.CharField(max_length=123, null=True, blank=True)
    tiktok = models.CharField(max_length=123, null=True, blank=True)
    facebook = models.CharField(max_length=123, null=True, blank=True)

    def __str__(self):
        return self.phone

class Banner(models.Model):
    image = models.ImageField(upload_to='account/banner_image/')

    def __str__(self):
        return 'banner'


class Carta(models.Model):
    user_carta_name = models.CharField(max_length=123)
    bank_name = models.CharField(max_length=123)
    carta_number = models.CharField(max_length=123)
    bank_number = models.IntegerField()
    modified_date = models.DateTimeField(auto_now=True)
    created_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user_carta_name}  --->  {self.bank_name}"

