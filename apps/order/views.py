from rest_framework import viewsets, generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from apps.order.models import (
    Order,
    CartItem,
    Promo
)
from apps.order.serializers import (PromoSerializer,
                                    PromoPostSerializer,
                                    CartItemSerializer, CartItemPostSerializer,
                                    OrderSerializer,
                                    OrderPostSerializer
                                    )
from apps.product.utils import CreateViewSetMixin


class PromoCreateView(generics.CreateAPIView):
    queryset = Promo.objects.all()
    serializer_class = PromoPostSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        # Yaratilayotgan promo foydalanuvchi bilan bog'lanadi
        serializer.save(user=self.request.user)


class CheckPromo(generics.ListCreateAPIView):
    queryset = Promo.objects.all()
    serializer_class = PromoSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        user = request.user

        # Serializerni user bilan chaqirish
        serializer = self.serializer_class(data=request.data, context={'user': user})
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CartItemViewSet(CreateViewSetMixin, viewsets.ModelViewSet):
    model = CartItem
    serializer_class = CartItemSerializer
    serializer_post_class = CartItemPostSerializer
    queryset = CartItem.objects.all()
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return CartItem.objects.filter(user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({'deleted': True}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['delete'], url_path='clear-cart')
    def clear_cart(self, request):
        user_cart_items = self.get_queryset()
        deleted_count = user_cart_items.count()
        user_cart_items.delete()
        return Response(
            {'message': f'{deleted_count} ta mahsulot savatchadan o\'chirildi.'},
            status=status.HTTP_200_OK
        )


class OrderViewSet(CreateViewSetMixin, viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    model = Order
    serializer_post_class = OrderPostSerializer
    queryset = Order.objects.all()
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    permission_classes = (IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        items_raw = request.data.get("items", [])
        
        # Items ni parse qilish (string yoki list bo'lishi mumkin)
        if isinstance(items_raw, str):
            # String format: "1,2,3"
            try:
                items_list = [int(i) for i in items_raw.split(",") if i.strip().isdigit()]
            except ValueError:
                raise ValidationError("Noto'g'ri item ID berilgan.")
        elif isinstance(items_raw, list):
            # List format: [1,2,3] yoki ["1","2","3"]
            try:
                items_list = [int(i) for i in items_raw]
            except (ValueError, TypeError):
                raise ValidationError("Noto'g'ri item ID berilgan.")
        else:
            raise ValidationError("Items parametri string yoki list bo'lishi kerak.")

        # Data ni dict sifatida tayyorlash
        promo_value = request.data.get('promo')
        data = {
            'items': items_list,
            'user': request.user.id,
            'location': request.data.get('location'),
            'promo': promo_value if promo_value else None,
        }
        
        # File mavjud bo'lsa qo'shish
        if 'file' in request.data:
            data['file'] = request.data.get('file')

        serializer = self.get_serializer(data=data, context={'request': request})
        if serializer.is_valid():
            order = serializer.save()

            # Mahsulot miqdorini kamaytirish
            cart_items = CartItem.objects.filter(id__in=items_list, user=request.user)
            if cart_items.count() != len(items_list):
                order.delete()
                raise ValidationError("Ba'zi itemlar mavjud emas yoki noto‘g‘ri ID berilgan.")

            for item in cart_items:
                product = item.product
                if item.quantity > product.quantity:
                    order.delete()
                    raise ValidationError(
                        f"{product.name} mahsulotidan yetarli miqdorda mavjud emas. "
                        f"Qoldiq: {product.quantity} ta."
                    )
                product.quantity -= item.quantity
                product.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        # Agar foydalanuvchi superuser bo'lsa, barcha orderlarni qaytaramiz
        if self.request.user.is_superuser:
            return self.queryset
        # Aks holda faqat o'zining orderlarini qaytaramiz
        return self.queryset.filter(user=self.request.user)

    def get_serializer_context(self):
        # Request obyektini serializer kontekstiga uzatish
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {"detail": "Buyurtma muvaffaqiyatli o'chirildi."},
            status=status.HTTP_204_NO_CONTENT
        )

    def perform_destroy(self, instance):
        instance.delete()


class OrderPDFView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id)

            if order.status == 'delivered':
                pdf_response = order.generate_pdf_receipt()
                if pdf_response:
                    return pdf_response
                return Response({"detail": "PDF yaratishda xatolik."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            return Response({"detail": "Buyurtma hali yetkazilmagan."}, status=status.HTTP_400_BAD_REQUEST)

        except Order.DoesNotExist:
            return Response({"detail": "Buyurtma topilmadi."}, status=status.HTTP_404_NOT_FOUND)


class MarkOrderAsDelivered(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk=None):
        try:
            order = Order.objects.get(pk=pk, user=request.user)
            order.status = 'delivered'
            order.save()

            pdf_response = order.generate_pdf_receipt()
            if pdf_response:
                return pdf_response
            return Response({"detail": "Buyurtma yetkazildi deb belgilandi."}, status=status.HTTP_200_OK)
        except Order.DoesNotExist:
            return Response({'error': 'Buyurtma topilmadi'}, status=status.HTTP_404_NOT_FOUND)
