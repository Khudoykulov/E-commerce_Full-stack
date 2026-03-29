from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .validators import validate_phone_number
from rest_framework.validators import UniqueValidator
from rest_framework.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password, password_validators_help_texts
from apps.account.models import User, UserToken
from .models import UserLocation, NewBlock, Advice, Call, Banner, Carta
from django.contrib.auth import get_user_model


class UserRegisterSerializer(serializers.ModelSerializer):
    phone = serializers.CharField(
        max_length=11, required=True,
        validators=[
            UniqueValidator(queryset=User.objects.all()),
        ]
    )
    password1 = serializers.CharField(write_only=True, validators=[validate_password],
                                      help_text=password_validators_help_texts())
    password2 = serializers.CharField(write_only=True)

    def validate_phone(self, value):
        if User.objects.filter(phone=value).exists():
            raise serializers.ValidationError("Telefon raqami allaqachon ishlatilgan.")
        return value

    def validate(self, attrs):
        password1 = attrs.get('password1')
        password2 = attrs.get('password2')
        if password1 != password2:
            raise ValidationError({'password2': 'Parollar mos kelmadi'})
        return attrs

    class Meta:
        model = User
        fields = ['name', 'phone', 'password1', 'password2']

    def create(self, validated_data):
        user = User.objects.create_user(
            name=validated_data['name'],
            phone=validated_data['phone'],
            password=validated_data['password1']
        )
        user.is_active = True
        user.save()
        return user


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['name'] = user.name
        token['created_date'] = user.created_date.strftime('%d.%m.%Y %H:%M:%S')
        return token


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id', 'name', 'phone', 'avatar', 'is_active', 'is_superuser', 'is_staff', 'modified_date',
            'created_date')


class SuperUserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('phone', 'name', 'password')

    def create(self, validated_data):
        validated_data['is_superuser'] = True
        validated_data['is_staff'] = True
        validated_data['is_active'] = True
        user = User.objects.create_superuser(**validated_data)
        return user


class UserLocationSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer(read_only=True)
    has_coordinates = serializers.BooleanField(read_only=True)

    class Meta:
        model = UserLocation
        fields = ['id', 'user', 'location', 'latitude', 'longitude', 'floor', 'apartment',
                  'has_coordinates', 'modified_date', 'created_date']
        read_only_fields = ['has_coordinates', 'modified_date', 'created_date']

    def validate_latitude(self, value):
        """Kenglikni validatsiya qilish"""
        if value:
            try:
                lat = float(value)
                if not -90 <= lat <= 90:
                    raise serializers.ValidationError("Kenglik -90 va 90 orasida bo'lishi kerak")
            except ValueError:
                raise serializers.ValidationError("Kenglik son bo'lishi kerak")
        return value

    def validate_longitude(self, value):
        """Uzunlikni validatsiya qilish"""
        if value:
            try:
                lng = float(value)
                if not -180 <= lng <= 180:
                    raise serializers.ValidationError("Uzunlik -180 va 180 orasida bo'lishi kerak")
            except ValueError:
                raise serializers.ValidationError("Uzunlik son bo'lishi kerak")
        return value

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user_id'] = user.id
        return super().create(validated_data)


class UserLocationMiniSerializer(serializers.ModelSerializer):
    """Manzil uchun qisqacha serializer (profil ichida ishlatish uchun)"""
    class Meta:
        model = UserLocation
        fields = ['id', 'location', 'latitude', 'longitude', 'floor', 'apartment']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'phone', 'avatar', ]


class UserProfileFullSerializer(serializers.ModelSerializer):
    """To'liq profil ma'lumotlari - manzillar va statistika bilan"""
    locations = serializers.SerializerMethodField()
    orders_count = serializers.SerializerMethodField()
    wishlist_count = serializers.SerializerMethodField()
    cart_items_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'name', 'phone', 'avatar', 'is_active', 'is_superuser', 'is_staff',
                  'locations', 'orders_count', 'wishlist_count', 'cart_items_count',
                  'modified_date', 'created_date']

    def get_locations(self, obj):
        locations = UserLocation.objects.filter(user=obj)
        return UserLocationMiniSerializer(locations, many=True).data

    def get_orders_count(self, obj):
        from apps.order.models import Order
        return Order.objects.filter(user=obj).count()

    def get_wishlist_count(self, obj):
        from apps.product.models import Wishlist
        return Wishlist.objects.filter(user=obj).count()

    def get_cart_items_count(self, obj):
        from apps.order.models import CartItem
        return CartItem.objects.filter(user=obj).count()


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['name', 'phone', 'avatar']

class UserDeleteSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=128, required=True)

    class Meta:
        model = User
        fields = ['password',]

    def validate_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Noto'g'ri parol")
        return value


class PasswordChangeSerializer(serializers.Serializer):
    """Parolni o'zgartirish uchun serializer"""
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(required=True, write_only=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Joriy parol noto'g'ri")
        return value

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({"new_password_confirm": "Yangi parollar mos kelmaydi"})
        return attrs

    def save(self):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


# NewBlock Serializer
class NewBlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewBlock
        fields = ['id', 'title_en', 'title_ru', 'title_uz', 'title_ko', 'description_en', 'description_ru', 'description_uz', 'description_ko', 'image', 'created_date']

# Advice Serializer
class AdviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Advice
        fields = ['id', 'title_en', 'title_ru', 'title_uz', 'title_ko', 'description_en', 'description_ru', 'description_uz', 'description_ko']


class CallSerializer(serializers.ModelSerializer):
    class Meta:
        model = Call
        fields = ['id', 'phone', 'telegram', 'instagram', 'tiktok', 'facebook']


class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = ['id', 'image']


class CartaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Carta
        fields = ['id', 'user_carta_name', 'bank_name', 'carta_number', 'bank_number']
