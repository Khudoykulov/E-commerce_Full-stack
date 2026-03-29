from django.urls import path, include
from rest_framework.routers import DefaultRouter

from apps.order.views import (
    CheckPromo,
    PromoCreateView,
    CartItemViewSet,
    OrderViewSet, OrderPDFView, MarkOrderAsDelivered,
)

router = DefaultRouter()
router.register('cart-items', CartItemViewSet, basename='cart-items')
router.register('', OrderViewSet, basename='order')


urlpatterns = [
    path('check_promo/', CheckPromo.as_view()),
    path('promo/create/', PromoCreateView.as_view(), name='promo-create'),
    path('order/<int:order_id>/receipt/', OrderPDFView.as_view(), name='order-pdf'),
    path('orders/mark_as_delivered/<int:pk>/', MarkOrderAsDelivered.as_view(), name='mark_as_delivered'),
    path('', include(router.urls)),
]