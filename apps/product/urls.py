from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    CategoryViewSet,
    TagViewSet,
    ProductViewSet,
    ProductImageViewSet,
    # TradeViewSet,
    WishlistViewSet,
    LikeViewSet,
    RankViewSet,
    CommentViewSet,
    CommentImageViewSet,
    BestSellingProductsAPIView,
    NewlyAddedProductsAPIView
)

router = DefaultRouter()
router.register('categories', CategoryViewSet)
# router.register('tags', TagViewSet)
# router.register('images', ProductImageViewSet)
# router.register('comment/images', CommentImageViewSet)
# router.register('trades', TradeViewSet)
router.register('wishlists', WishlistViewSet)
router.register('likes', LikeViewSet)
router.register('(?P<pid>[0-9]+)/ranks', RankViewSet)
# router.register('(?P<pid>[0-9]+)/comments', CommentViewSet)
router.register('', ProductViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('best-selling/', BestSellingProductsAPIView.as_view(), name='best-selling-products'),
    path('newly-added/', NewlyAddedProductsAPIView.as_view(), name='newly-added-products')
]