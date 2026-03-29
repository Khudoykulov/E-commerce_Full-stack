from django.shortcuts import get_object_or_404
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, generics, status, permissions
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from .utils import CreateViewSetMixin
from .models import (
    Category,
    Tag,
    Product,
    ProductImage,
    # Trade,
    Wishlist,
    Like,
    Comment, Rank, CommentImage,
)
from .serializers import (
    CategorySerializer,
    TagSerializer,
    ProductSerializer,
    ProductPostSerializer,
    ProductImageSerializer,
    # TradeSerializer,
    # TradePostSerializer,
    WishListSerializer,
    WishListPostSerializer,
    LikeSerializer,
    LikePostSerializer,
    RankSerializer,
    CommentImageSerializer,
    CommentSerializer,
)
from .permissions import (
    IsAdminOrReadOnly,
    IsAuthor,
)
from .filters import ProductFilter


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]  # Public endpoint
    filter_backends = (SearchFilter,)
    search_fields = ['name', 'name_uz', 'name_ru', 'name_en', 'name_ko']
    parser_classes = (MultiPartParser, FormParser)

    def get_queryset(self):
        return Category.objects.filter(parent__isnull=True)

    def get_object(self):
        # Retrieve uchun barcha kategoriyalardan izlash (parent ham, child ham)
        queryset = Category.objects.all()
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        assert lookup_url_kwarg in self.kwargs, (
                'Expected view %s to be called with a URL keyword argument '
                'named "%s". Fix your URL conf, or set the `.lookup_field` '
                'attribute on the view correctly.' %
                (self.__class__.__name__, lookup_url_kwarg)
        )
        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
        obj = get_object_or_404(queryset, **filter_kwargs)
        self.check_object_permissions(self.request, obj)
        return obj

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({'deleted': True}, status=status.HTTP_200_OK)


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.AllowAny]  # Public endpoint
    filter_backends = (SearchFilter,)
    search_fields = ['name']

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({'deleted': True}, status=status.HTTP_200_OK)


class ProductViewSet(CreateViewSetMixin, viewsets.ModelViewSet):
    queryset = Product.objects.all()
    model = Product
    parser_classes = (MultiPartParser, FormParser)
    serializer_class = ProductSerializer
    serializer_post_class = ProductPostSerializer
    permission_classes = [permissions.AllowAny]  # Public endpoint
    filter_backends = (SearchFilter, DjangoFilterBackend, OrderingFilter)
    filterset_class = ProductFilter
    search_fields = ['name', 'name_uz', 'name_ru', 'name_en', 'name_ko',
                     'description', 'description_uz', 'description_ru',
                     'description_en', 'description_ko', 'category__name']
    ordering_fields = ['views', 'id', 'sold_count', 'price', 'discount', 'created_date']
    ordering = ['-created_date']

    def get_queryset(self):
        queryset = super().get_queryset()

        # Qo'shimcha qidiruv parametri
        search_query = self.request.query_params.get('q', None)
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(name_uz__icontains=search_query) |
                Q(name_ru__icontains=search_query) |
                Q(name_en__icontains=search_query) |
                Q(name_ko__icontains=search_query) |
                Q(description__icontains=search_query) |
                Q(category__name__icontains=search_query)
            )

        return queryset

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({'deleted': True}, status=status.HTTP_200_OK)


class ProductImageViewSet(viewsets.ModelViewSet):
    queryset = ProductImage.objects.all()
    # parser_classes = (MultiPartParser, FormParser)<
    serializer_class = ProductImageSerializer
    permission_classes = [permissions.AllowAny]  # Public endpoint

    def get_serializer_context(self):
        pid = self.kwargs.get('pid')
        ctx = super().get_serializer_context()
        ctx['pid'] = pid
        return ctx

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({'deleted': True}, status=status.HTTP_200_OK)


class BestSellingProductsAPIView(generics.ListAPIView):
    queryset = Product.objects.order_by('-sold_count')  # Ko'p sotilganlarni kamayish tartibida /
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]  # Public endpoint


class NewlyAddedProductsAPIView(generics.ListAPIView):
    queryset = Product.objects.order_by('-created_date')  # Yangi qo‘shilganlarni kamayish tartibida
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]  # Public endpoint

# class TradeViewSet(CreateViewSetMixin, viewsets.ModelViewSet):
#     queryset = Trade.objects.all()
#     model = Trade
#     serializer_class = TradeSerializer
#     serializer_post_class = TradePostSerializer
#     permission_classes = [permissions.IsAdminUser]
#     filter_backends = (SearchFilter, DjangoFilterBackend)
#     search_fields = ['product__name']
#     filterset_fields = ['action', 'product']
#
#     def destroy(self, request, *args, **kwargs):
#         instance = self.get_object()
#         self.perform_destroy(instance)
#         return Response({'deleted': True}, status=status.HTTP_200_OK)


class WishlistViewSet(CreateViewSetMixin, viewsets.ModelViewSet):
    model = Wishlist
    queryset = Wishlist.objects.all()
    serializer_class = WishListSerializer
    serializer_post_class = WishListPostSerializer
    permission_classes = [IsAuthor | IsAdminOrReadOnly]
    filter_backends = [SearchFilter, DjangoFilterBackend]
    search_fields = ['product__name']

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.is_superuser:
            return qs.all()
        return qs.filter(user_id=self.request.user.id)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({'deleted': True}, status=status.HTTP_200_OK)


class LikeViewSet(CreateViewSetMixin, viewsets.ModelViewSet):
    model = Like
    queryset = Like.objects.all()
    serializer_class = LikeSerializer
    serializer_post_class = LikePostSerializer
    permission_classes = [IsAuthor | IsAdminOrReadOnly]
    filter_backends = [SearchFilter, DjangoFilterBackend]
    search_fields = ['product__name']

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.user.is_superuser:
            return qs.all()
        return qs.filter(user_id=self.request.user.id)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({'deleted': True}, status=status.HTTP_200_OK)


class RankViewSet(viewsets.ModelViewSet):
    queryset = Rank.objects.all()
    serializer_class = RankSerializer
    filter_backends = [SearchFilter, DjangoFilterBackend]
    search_fields = ['product__name']

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Rank.objects.all()
        return Rank.objects.none()

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['pid'] = self.kwargs.get('pid')
        return ctx

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({'deleted': True}, status=status.HTTP_200_OK)


class CommentImageViewSet(viewsets.ModelViewSet):
    queryset = CommentImage.objects.all()
    parser_classes = (MultiPartParser, FormParser)
    serializer_class = CommentImageSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({'deleted': True}, status=status.HTTP_200_OK)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.filter(parent__isnull=True)
    serializer_class = CommentSerializer
    permission_classes = [IsAuthor]

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx['pid'] = self.kwargs.get('pid')
        return ctx

    def update(self, request, *args, **kwargs):
        pass

    def get_object(self):
        queryset = self.queryset
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        assert lookup_url_kwarg in self.kwargs, (
                'Expected view %s to be called with a URL keyword argument '
                'named "%s". Fix your URL conf, or set the `.lookup_field` '
                'attribute on the view correctly.' %
                (self.__class__.__name__, lookup_url_kwarg)
        )
        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
        obj = get_object_or_404(queryset, **filter_kwargs)
        self.check_object_permissions(self.request, obj)
        return obj

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({'deleted': True}, status=status.HTTP_200_OK)
