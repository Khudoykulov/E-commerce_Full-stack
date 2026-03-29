import django_filters
from .models import Product, Category


class ProductFilter(django_filters.FilterSet):
    """Mahsulotlar uchun kengaytirilgan filter"""

    # Kategoriya bo'yicha filter (parent kategoriya ham, child ham)
    category = django_filters.NumberFilter(method='filter_category')
    category_name = django_filters.CharFilter(field_name='category__name', lookup_expr='icontains')

    # Narx bo'yicha filter
    min_price = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='price', lookup_expr='lte')

    # Chegirma bo'yicha filter
    min_discount = django_filters.NumberFilter(field_name='discount', lookup_expr='gte')
    max_discount = django_filters.NumberFilter(field_name='discount', lookup_expr='lte')
    has_discount = django_filters.BooleanFilter(method='filter_has_discount')

    # Mavjudlik bo'yicha filter
    in_stock = django_filters.BooleanFilter(method='filter_in_stock')

    # Nom bo'yicha filter (barcha tillarda)
    name = django_filters.CharFilter(method='filter_name')

    class Meta:
        model = Product
        fields = ['category', 'category_name', 'min_price', 'max_price',
                  'min_discount', 'max_discount', 'has_discount', 'in_stock', 'name']

    def filter_category(self, queryset, name, value):
        """Kategoriya bo'yicha filter - parent kategoriya bo'lsa child kategoriyalarni ham qo'shish"""
        if not value:
            return queryset
        
        try:
            category = Category.objects.get(id=value)
            # Agar parent kategoriya bo'lsa, uning barcha child kategoriyalarini olish
            if category.children.exists():
                # Parent kategoriya - child kategoriyalaridagi mahsulotlarni olish
                child_ids = list(category.children.values_list('id', flat=True))
                child_ids.append(category.id)  # Parent kategoriyani ham qo'shamiz (agar unda to'g'ridan-to'g'ri mahsulot bo'lsa)
                return queryset.filter(category_id__in=child_ids)
            else:
                # Oddiy kategoriya yoki child kategoriya - to'g'ridan-to'g'ri filtrlash
                return queryset.filter(category_id=value)
        except Category.DoesNotExist:
            return queryset.none()

    def filter_has_discount(self, queryset, name, value):
        """Chegirmali mahsulotlarni filter qilish"""
        if value is True:
            return queryset.filter(discount__gt=0)
        elif value is False:
            return queryset.filter(discount=0)
        return queryset

    def filter_in_stock(self, queryset, name, value):
        """Mavjud mahsulotlarni filter qilish"""
        if value is True:
            return queryset.filter(quantity__gt=0)
        elif value is False:
            return queryset.filter(quantity=0)
        return queryset

    def filter_name(self, queryset, name, value):
        """Barcha tillardagi nomlar bo'yicha qidirish"""
        from django.db.models import Q
        return queryset.filter(
            Q(name__icontains=value) |
            Q(name_uz__icontains=value) |
            Q(name_ru__icontains=value) |
            Q(name_en__icontains=value) |
            Q(name_ko__icontains=value)
        )
