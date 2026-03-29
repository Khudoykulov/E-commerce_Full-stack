from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from apps.account.models import User, UserLocation
from apps.account.serializers import UserLocationSerializer
from apps.order.models import (
    Order,
    CartItem,
    Promo,
)
from apps.product.serializers import ProductSerializer
from drf_spectacular.utils import extend_schema_field


class PromoSerializer(serializers.Serializer):
    name = serializers.CharField()

    def validate(self, attrs):
        user = self.context.get('user')
        name = attrs.get('name')
        if name is None:
            raise ValidationError({'detail': "Name is required"})
        promo = Promo.objects.filter(name=name)
        if not promo.exists():
            raise ValidationError({'detail': "Promo does not exist"})
        if promo.last().is_expired:
            raise ValidationError({'detail': "Promo is expired"})
        if user in promo.last().members.all():
            raise ValidationError({'detail': "Promo is already used"})
        return attrs


class PromoPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Promo
        fields = ['id', 'name', 'user', 'description', 'discount', 'min_price', 'expire_date', 'is_expired',
                  'created_date']
        read_only_fields = ['id', 'created_date', 'is_expired']

    def validate(self, attrs):
        # Foydalanuvchi promo yaratganida chegirma va minimal narxni tekshirish
        discount = attrs.get('discount', 0)
        min_price = attrs.get('min_price', 0)

        if discount <= 0 or discount > 100:
            raise serializers.ValidationError({'discount': "Chegirma 1 dan 100 gacha bo'lishi kerak."})
        if min_price < 100.00:
            raise serializers.ValidationError({'min_price': "Minimal narx kamida 100 bo'lishi kerak."})

        return attrs


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    get_amount = serializers.FloatField(read_only=True)

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'user', 'quantity', 'get_amount', 'created_date']
        read_only_fields = ['user', 'created_date']
        extra_kwargs = {
            'product': {'required': True},
            'quantity': {'required': True},
        }


class CartItemPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'user', 'quantity', 'get_amount', 'created_date']
        read_only_fields = ['user', 'created_date']
        extra_kwargs = {
            'product': {'required': True},
            'quantity': {'required': True},
        }

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user_id'] = user.id
        return super().create(validated_data)


class UserSerializersOrder(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'phone']


class OrderSerializer(serializers.ModelSerializer):
    user = UserSerializersOrder(read_only=True)
    items_data = serializers.JSONField(read_only=True)  # Yangi qo'shilgan maydon
    promo = serializers.CharField(required=False, allow_blank=True)
    status = serializers.CharField(source='get_status_display')

    class Meta:
        model = Order
        fields = ['id', 'user', 'location_data', 'file', 'items_data', 'promo', 'get_amount', 'status', 'payment_confirmed', 'modified_date',
                  'created_date']


class OrderPostSerializer(serializers.ModelSerializer):
    items = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True
    )
    location = serializers.PrimaryKeyRelatedField(queryset=UserLocation.objects.all(), required=False)

    class Meta:
        model = Order
        fields = ['id', 'user', 'items', 'promo', 'location', 'file', 'get_amount', 'modified_date', 'created_date']
        read_only_fields = ['user', 'get_amount']

    def validate(self, attrs):
        user = self.context.get('request').user
        location_id = self.context['request'].data.get('location')

        if location_id:
            try:
                location = UserLocation.objects.get(id=location_id, user=user)
            except UserLocation.DoesNotExist:
                raise ValidationError("Berilgan joylashuv mavjud emas yoki sizga tegishli emas.")
        else:
            location = UserLocation.objects.filter(user=user).last()
            if not location:
                raise ValidationError("Joylashuv topilmadi. Iltimos, joylashuv qo'shing.")

        attrs['location'] = location

        # Promo kodni tekshirish
        promo_code = attrs.get('promo', None)
        if promo_code:
            try:
                promo = Promo.objects.get(name=promo_code)
                if promo.is_expired:
                    raise ValidationError("Promo kodning muddati o'tgan.")

                # CartItem larni olish va umumiy summani hisoblash
                items_ids = attrs.get('items', [])
                cart_items = CartItem.objects.filter(id__in=items_ids, user=user)
                total_amount = sum(item.get_amount for item in cart_items)

                if total_amount < float(promo.min_price):
                    raise ValidationError(
                        f"Promo kodni ishlatish uchun buyurtma miqdori {promo.min_price} dan kam bo'lmasligi kerak.")
                if promo.members.filter(id=user.id).exists():
                    raise ValidationError("Siz bu promo kodni allaqachon ishlatgansiz.")
                promo.members.add(user)
                promo.save()
            except Promo.DoesNotExist:
                raise ValidationError("Promo kod mavjud emas.")

        return attrs

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        items = validated_data.pop('items', [])
        order = super().create(validated_data)

        # items_data ni to'ldirish
        cart_items = CartItem.objects.filter(id__in=items)
        if cart_items.count() != len(items):
            order.delete()
            raise ValidationError("Ba'zi itemlar mavjud emas yoki noto‘g‘ri ID berilgan.")

        order.items_data = [
            {
                'id': item.id,
                'product_id': item.product.id,
                'product_name': item.product.name,
                'product_image': item.product.images.first().image.url if item.product.images.exists() else None,
                'quantity': item.quantity,
                'original_price': str(item.product.price),  # Asl narx
                'discount_percent': item.product.discount,  # Chegirma foizi
                'discounted_price': str(item.product.discounted_price),  # Chegirmadan keyingi narx
                'price': str(item.get_amount),  # Umumiy summa (chegirma * miqdor)
            } for item in cart_items
        ]
        order.save()

        # items ni ManyToManyField ga qo'shish
        for item in cart_items:
            order.items.add(item)

        return order

    def update(self, instance, validated_data):
        items = validated_data.pop('items', None)
        instance = super().update(instance, validated_data)

        if items:
            cart_items = CartItem.objects.filter(id__in=items)
            if cart_items.count() != len(items):
                raise ValidationError("Ba'zi itemlar mavjud emas yoki noto‘g‘ri ID berilgan.")

            instance.items_data = [
                {
                    'id': item.id,
                    'product_id': item.product.id,
                    'product_name': item.product.name,
                    'product_image': item.product.images.first().image.url if item.product.images.exists() else None,
                    'quantity': item.quantity,
                    'original_price': str(item.product.price),
                    'discount_percent': item.product.discount,
                    'discounted_price': str(item.product.discounted_price),
                    'price': str(item.get_amount),
                } for item in cart_items
            ]
            instance.items.clear()  # Eski items ni o'chirish
            for item in cart_items:
                instance.items.add(item)  # Yangi items ni qo'shish
            instance.save()

        return instance
