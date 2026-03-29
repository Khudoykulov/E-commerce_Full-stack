"""
Frontend Views - Django Template Views
API orqali backend bilan ishlaydi
"""
from django.shortcuts import render, redirect
from django.views import View
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from .api_client import APIClient


class BaseView(View):
    """Base view class with common functionality"""

    def get_api_client(self, request):
        return APIClient(request)

    def get_common_context(self, request):
        """Har bir sahifa uchun umumiy context"""
        api = self.get_api_client(request)
        context = {
            'is_authenticated': 'access_token' in request.session,
            'cart_count': 0,
            'base_url': api.base_url,
        }

        # Cart count
        if context['is_authenticated']:
            cart_response = api.get_cart()
            if not cart_response.get('error'):
                cart_data = cart_response.get('data', {})
                if isinstance(cart_data, dict):
                    context['cart_count'] = len(cart_data.get('results', []))
                elif isinstance(cart_data, list):
                    context['cart_count'] = len(cart_data)

        # Categories for navbar
        cat_response = api.get_categories()
        if not cat_response.get('error'):
            cat_data = cat_response.get('data', {})
            if isinstance(cat_data, dict):
                context['nav_categories'] = cat_data.get('results', [])[:8]
            elif isinstance(cat_data, list):
                context['nav_categories'] = cat_data[:8]
            else:
                context['nav_categories'] = []
        else:
            context['nav_categories'] = []

        return context

    def get_account_context(self, request):
        """Account sahifalari uchun umumiy context (profil + sidebar)"""
        context = self.get_common_context(request)
        api = self.get_api_client(request)

        # Profil ma'lumotlari (sidebar uchun)
        profile_response = api.get_profile()
        if not profile_response.get('error'):
            context['profile'] = profile_response.get('data', {})
        else:
            context['profile'] = {}

        return context


class HomeView(BaseView):
    """Bosh sahifa"""
    template_name = 'frontend/home.html'

    def get(self, request):
        api = self.get_api_client(request)
        context = self.get_common_context(request)

        # Banners
        banners_response = api.get_banners()
        if not banners_response.get('error'):
            banners_data = banners_response.get('data', {})
            if isinstance(banners_data, dict):
                context['banners'] = banners_data.get('results', [])
            elif isinstance(banners_data, list):
                context['banners'] = banners_data
            else:
                context['banners'] = []
        else:
            context['banners'] = []

        # Categories
        cat_response = api.get_categories()
        if not cat_response.get('error'):
            cat_data = cat_response.get('data', {})
            if isinstance(cat_data, dict):
                context['categories'] = cat_data.get('results', [])
            elif isinstance(cat_data, list):
                context['categories'] = cat_data
            else:
                context['categories'] = []
        else:
            context['categories'] = []

        # Best selling products
        best_response = api.get_best_selling(limit=8)
        if not best_response.get('error'):
            best_data = best_response.get('data', {})
            if isinstance(best_data, dict):
                context['best_products'] = best_data.get('results', [])
            elif isinstance(best_data, list):
                context['best_products'] = best_data
            else:
                context['best_products'] = []
        else:
            context['best_products'] = []

        # Newly added products
        new_response = api.get_newly_added(limit=8)
        if not new_response.get('error'):
            new_data = new_response.get('data', {})
            if isinstance(new_data, dict):
                context['new_products'] = new_data.get('results', [])
            elif isinstance(new_data, list):
                context['new_products'] = new_data
            else:
                context['new_products'] = []
        else:
            context['new_products'] = []

        return render(request, self.template_name, context)


class ProductListView(BaseView):
    """Mahsulotlar ro'yxati"""
    template_name = 'frontend/products/list.html'

    def get(self, request):
        api = self.get_api_client(request)
        context = self.get_common_context(request)

        # Query params
        search = request.GET.get('search', '')
        category = request.GET.get('category', '')
        ordering = request.GET.get('ordering', '-id')
        page = int(request.GET.get('page', 1))
        limit = 12
        offset = (page - 1) * limit

        # Get products
        products_response = api.get_products(
            search=search,
            category=category if category else None,
            ordering=ordering,
            limit=limit,
            offset=offset
        )

        if not products_response.get('error'):
            products_data = products_response.get('data', {})
            if isinstance(products_data, dict):
                context['products'] = products_data.get('results', [])
                context['total_count'] = products_data.get('count', 0)
                context['has_next'] = products_data.get('next') is not None
                context['has_prev'] = products_data.get('previous') is not None
            elif isinstance(products_data, list):
                context['products'] = products_data
                context['total_count'] = len(products_data)
                context['has_next'] = False
                context['has_prev'] = False
            else:
                context['products'] = []
                context['total_count'] = 0
                context['has_next'] = False
                context['has_prev'] = False
        else:
            context['products'] = []
            context['total_count'] = 0
            context['has_next'] = False
            context['has_prev'] = False

        # Categories for filter
        cat_response = api.get_categories()
        if not cat_response.get('error'):
            cat_data = cat_response.get('data', {})
            if isinstance(cat_data, dict):
                context['categories'] = cat_data.get('results', [])
            elif isinstance(cat_data, list):
                context['categories'] = cat_data
            else:
                context['categories'] = []
        else:
            context['categories'] = []

        context['search'] = search
        context['current_category'] = category
        context['ordering'] = ordering
        context['current_page'] = page
        context['total_pages'] = (context['total_count'] + limit - 1) // limit if context['total_count'] > 0 else 1

        return render(request, self.template_name, context)


class ProductDetailView(BaseView):
    """Mahsulot detallari"""
    template_name = 'frontend/products/detail.html'

    def get(self, request, pk):
        api = self.get_api_client(request)
        context = self.get_common_context(request)

        # Get product
        product_response = api.get_product(pk)
        if product_response.get('error'):
            messages.error(request, 'Mahsulot topilmadi')
            return redirect('frontend:product_list')

        context['product'] = product_response.get('data', {})

        # Related products (same category)
        if context['product'].get('category'):
            related_response = api.get_products(
                category=context['product']['category'].get('id'),
                limit=4
            )
            if not related_response.get('error'):
                related_data = related_response.get('data', {})
                if isinstance(related_data, dict):
                    all_related = related_data.get('results', [])
                elif isinstance(related_data, list):
                    all_related = related_data
                else:
                    all_related = []
                # Exclude current product
                context['related_products'] = [p for p in all_related if p.get('id') != pk][:4]
            else:
                context['related_products'] = []
        else:
            context['related_products'] = []

        return render(request, self.template_name, context)


class CategoryView(BaseView):
    """Kategoriya sahifasi"""
    template_name = 'frontend/products/list.html'

    def get(self, request, pk):
        api = self.get_api_client(request)
        context = self.get_common_context(request)

        # Get category info
        cat_response = api.get_category(pk)
        if cat_response.get('error'):
            messages.error(request, 'Kategoriya topilmadi')
            return redirect('frontend:home')

        context['current_category_info'] = cat_response.get('data', {})

        # Query params
        ordering = request.GET.get('ordering', '-id')
        page = int(request.GET.get('page', 1))
        limit = 12
        offset = (page - 1) * limit

        # Get products
        products_response = api.get_products(
            category=pk,
            ordering=ordering,
            limit=limit,
            offset=offset
        )

        if not products_response.get('error'):
            products_data = products_response.get('data', {})
            if isinstance(products_data, dict):
                context['products'] = products_data.get('results', [])
                context['total_count'] = products_data.get('count', 0)
                context['has_next'] = products_data.get('next') is not None
                context['has_prev'] = products_data.get('previous') is not None
            elif isinstance(products_data, list):
                context['products'] = products_data
                context['total_count'] = len(products_data)
                context['has_next'] = False
                context['has_prev'] = False
            else:
                context['products'] = []
                context['total_count'] = 0
                context['has_next'] = False
                context['has_prev'] = False
        else:
            context['products'] = []
            context['total_count'] = 0
            context['has_next'] = False
            context['has_prev'] = False

        # All categories for sidebar
        all_cat_response = api.get_categories()
        if not all_cat_response.get('error'):
            cat_data = all_cat_response.get('data', {})
            if isinstance(cat_data, dict):
                context['categories'] = cat_data.get('results', [])
            elif isinstance(cat_data, list):
                context['categories'] = cat_data
            else:
                context['categories'] = []
        else:
            context['categories'] = []

        context['current_category'] = str(pk)
        context['ordering'] = ordering
        context['current_page'] = page
        context['total_pages'] = (context['total_count'] + limit - 1) // limit if context['total_count'] > 0 else 1
        context['search'] = ''

        return render(request, self.template_name, context)


class CartView(BaseView):
    """Savatcha sahifasi"""
    template_name = 'frontend/cart.html'

    def get(self, request):
        if 'access_token' not in request.session:
            messages.warning(request, 'Savatchani ko\'rish uchun tizimga kiring')
            return redirect('frontend:login')

        api = self.get_api_client(request)
        context = self.get_common_context(request)

        # Get cart items
        cart_response = api.get_cart()
        if not cart_response.get('error'):
            cart_data = cart_response.get('data', {})
            if isinstance(cart_data, dict):
                context['cart_items'] = cart_data.get('results', [])
            elif isinstance(cart_data, list):
                context['cart_items'] = cart_data
            else:
                context['cart_items'] = []
        else:
            context['cart_items'] = []

        # Calculate total
        total = 0
        for item in context['cart_items']:
            amount = item.get('get_amount', 0)
            if amount:
                total += float(amount)
        context['cart_total'] = total

        return render(request, self.template_name, context)


class CartAddView(BaseView):
    """Savatchaga qo'shish (AJAX)"""

    def post(self, request):
        if 'access_token' not in request.session:
            return JsonResponse({'error': True, 'message': 'Tizimga kiring'}, status=401)

        api = self.get_api_client(request)
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity', 1))

        if not product_id:
            return JsonResponse({'error': True, 'message': 'Mahsulot tanlanmadi'}, status=400)

        response = api.add_to_cart(product_id, quantity)

        if response.get('error'):
            return JsonResponse({
                'error': True,
                'message': response.get('message', 'Xatolik yuz berdi')
            }, status=response.get('status_code', 400))

        return JsonResponse({
            'error': False,
            'message': 'Savatchaga qo\'shildi',
            'data': response.get('data')
        })


class CartUpdateView(BaseView):
    """Savatcha itemni yangilash (AJAX)"""

    def post(self, request, pk):
        if 'access_token' not in request.session:
            return JsonResponse({'error': True, 'message': 'Tizimga kiring'}, status=401)

        api = self.get_api_client(request)
        quantity = int(request.POST.get('quantity', 1))

        response = api.update_cart_item(pk, quantity)

        if response.get('error'):
            return JsonResponse({
                'error': True,
                'message': response.get('message', 'Xatolik yuz berdi')
            }, status=response.get('status_code', 400))

        return JsonResponse({
            'error': False,
            'message': 'Yangilandi',
            'data': response.get('data')
        })


class CartRemoveView(BaseView):
    """Savatchadan o'chirish (AJAX)"""

    def post(self, request, pk):
        if 'access_token' not in request.session:
            return JsonResponse({'error': True, 'message': 'Tizimga kiring'}, status=401)

        api = self.get_api_client(request)
        response = api.remove_from_cart(pk)

        if response.get('error'):
            return JsonResponse({
                'error': True,
                'message': response.get('message', 'Xatolik yuz berdi')
            }, status=response.get('status_code', 400))

        return JsonResponse({
            'error': False,
            'message': 'O\'chirildi'
        })


class CheckoutView(BaseView):
    """Checkout sahifasi"""
    template_name = 'frontend/checkout.html'

    def get(self, request):
        if 'access_token' not in request.session:
            messages.warning(request, 'Buyurtma berish uchun tizimga kiring')
            return redirect('frontend:login')

        api = self.get_api_client(request)
        context = self.get_common_context(request)

        # Get cart items
        cart_response = api.get_cart()
        if not cart_response.get('error'):
            cart_data = cart_response.get('data', {})
            if isinstance(cart_data, dict):
                context['cart_items'] = cart_data.get('results', [])
            elif isinstance(cart_data, list):
                context['cart_items'] = cart_data
            else:
                context['cart_items'] = []
        else:
            context['cart_items'] = []

        if not context['cart_items']:
            messages.warning(request, 'Savatchingiz bo\'sh')
            return redirect('frontend:cart')

        # Calculate total
        total = 0
        for item in context['cart_items']:
            amount = item.get('get_amount', 0)
            if amount:
                total += float(amount)
        context['cart_total'] = total

        # Get user locations
        locations_response = api.get_locations()
        if not locations_response.get('error'):
            loc_data = locations_response.get('data', {})
            if isinstance(loc_data, dict):
                context['locations'] = loc_data.get('results', [])
            elif isinstance(loc_data, list):
                context['locations'] = loc_data
            else:
                context['locations'] = []
        else:
            context['locations'] = []

        return render(request, self.template_name, context)

    def post(self, request):
        if 'access_token' not in request.session:
            return redirect('frontend:login')

        api = self.get_api_client(request)

        location_id = request.POST.get('location_id')
        promo = request.POST.get('promo', '')

        # Yangi manzil qo'shish
        if request.POST.get('new_location'):
            location_data = {
                'location': request.POST.get('address', ''),
                'latitude': request.POST.get('latitude', ''),
                'longitude': request.POST.get('longitude', ''),
                'floor': request.POST.get('floor', ''),
                'apartment': request.POST.get('apartment', ''),
            }
            loc_response = api.add_location(location_data)
            if not loc_response.get('error'):
                location_id = loc_response.get('data', {}).get('id')
            else:
                messages.error(request, 'Manzilni saqlashda xatolik')
                return redirect('frontend:checkout')

        if not location_id:
            messages.error(request, 'Manzilni tanlang')
            return redirect('frontend:checkout')

        # Get cart items
        cart_response = api.get_cart()
        if cart_response.get('error'):
            messages.error(request, 'Savatchani olishda xatolik')
            return redirect('frontend:cart')

        cart_data = cart_response.get('data', {})
        if isinstance(cart_data, dict):
            cart_items = cart_data.get('results', [])
        elif isinstance(cart_data, list):
            cart_items = cart_data
        else:
            cart_items = []

        if not cart_items:
            messages.error(request, 'Savatchingiz bo\'sh')
            return redirect('frontend:cart')

        # Create order
        item_ids = [item.get('id') for item in cart_items]
        order_response = api.create_order(
            items=item_ids,
            location_id=location_id,
            promo=promo if promo else None
        )

        if order_response.get('error'):
            messages.error(request, order_response.get('message', 'Buyurtma yaratishda xatolik'))
            return redirect('frontend:checkout')

        # Clear cart after successful order
        api.clear_cart()

        messages.success(request, 'Buyurtmangiz qabul qilindi!')
        return redirect('frontend:order_success')


class OrderSuccessView(BaseView):
    """Buyurtma muvaffaqiyatli sahifasi"""
    template_name = 'frontend/order_success.html'

    def get(self, request):
        context = self.get_common_context(request)
        return render(request, self.template_name, context)


# === Auth Views ===

class LoginView(BaseView):
    """Login sahifasi"""
    template_name = 'frontend/account/login.html'

    def get(self, request):
        if 'access_token' in request.session:
            return redirect('frontend:home')
        context = self.get_common_context(request)
        return render(request, self.template_name, context)

    def post(self, request):
        api = self.get_api_client(request)
        phone = request.POST.get('phone', '')
        password = request.POST.get('password', '')

        if not phone or not password:
            messages.error(request, 'Telefon va parolni kiriting')
            return render(request, self.template_name, self.get_common_context(request))

        response = api.login(phone, password)

        if response.get('error'):
            messages.error(request, response.get('message', 'Login xatosi'))
            return render(request, self.template_name, self.get_common_context(request))

        # Save tokens to session
        data = response.get('data', {})
        request.session['access_token'] = data.get('access')
        request.session['refresh_token'] = data.get('refresh')

        messages.success(request, 'Tizimga muvaffaqiyatli kirdingiz!')

        next_url = request.GET.get('next', '')
        if next_url:
            return redirect(next_url)
        return redirect('frontend:home')


class RegisterView(BaseView):
    """Ro'yxatdan o'tish sahifasi"""
    template_name = 'frontend/account/register.html'

    def get(self, request):
        if 'access_token' in request.session:
            return redirect('frontend:home')
        context = self.get_common_context(request)
        return render(request, self.template_name, context)

    def post(self, request):
        api = self.get_api_client(request)

        name = request.POST.get('name', '')
        phone = request.POST.get('phone', '')
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')

        if not all([name, phone, password1, password2]):
            messages.error(request, 'Barcha maydonlarni to\'ldiring')
            return render(request, self.template_name, self.get_common_context(request))

        if password1 != password2:
            messages.error(request, 'Parollar mos kelmadi')
            return render(request, self.template_name, self.get_common_context(request))

        response = api.register(name, phone, password1, password2)

        if response.get('error'):
            error_msg = response.get('message', 'Ro\'yxatdan o\'tishda xatolik')
            messages.error(request, error_msg)
            return render(request, self.template_name, self.get_common_context(request))

        messages.success(request, 'Muvaffaqiyatli ro\'yxatdan o\'tdingiz! Endi tizimga kiring.')
        return redirect('frontend:login')


class LogoutView(View):
    """Logout"""

    def get(self, request):
        request.session.flush()
        messages.success(request, 'Tizimdan chiqdingiz')
        return redirect('frontend:home')


class ProfileView(BaseView):
    """Profil sahifasi"""
    template_name = 'frontend/account/profile.html'

    def get(self, request):
        if 'access_token' not in request.session:
            return redirect('frontend:login')

        api = self.get_api_client(request)
        context = self.get_account_context(request)
        context['active_page'] = 'profile'

        # Profil ma'lumotlari allaqachon context'da
        if not context.get('profile'):
            messages.error(request, 'Profil ma\'lumotlarini olishda xatolik')
            return redirect('frontend:home')

        # Get locations
        locations_response = api.get_locations()
        if not locations_response.get('error'):
            loc_data = locations_response.get('data', {})
            if isinstance(loc_data, dict):
                context['locations'] = loc_data.get('results', [])
            elif isinstance(loc_data, list):
                context['locations'] = loc_data
            else:
                context['locations'] = []
        else:
            context['locations'] = []

        return render(request, self.template_name, context)

    def post(self, request):
        if 'access_token' not in request.session:
            return redirect('frontend:login')

        api = self.get_api_client(request)

        data = {
            'name': request.POST.get('name', ''),
            'phone': request.POST.get('phone', ''),
        }

        avatar = request.FILES.get('avatar')
        response = api.update_profile(data, avatar)

        if response.get('error'):
            messages.error(request, response.get('message', 'Profilni yangilashda xatolik'))
        else:
            messages.success(request, 'Profil yangilandi')

        return redirect('frontend:profile')


class OrdersView(BaseView):
    """Buyurtmalar ro'yxati"""
    template_name = 'frontend/account/orders.html'

    def get(self, request):
        if 'access_token' not in request.session:
            return redirect('frontend:login')

        api = self.get_api_client(request)
        context = self.get_account_context(request)
        context['active_page'] = 'orders'

        page = int(request.GET.get('page', 1))
        limit = 10
        offset = (page - 1) * limit

        orders_response = api.get_orders(limit=limit, offset=offset)
        if not orders_response.get('error'):
            orders_data = orders_response.get('data', {})
            if isinstance(orders_data, dict):
                context['orders'] = orders_data.get('results', [])
                context['total_count'] = orders_data.get('count', 0)
                context['has_next'] = orders_data.get('next') is not None
                context['has_prev'] = orders_data.get('previous') is not None
            elif isinstance(orders_data, list):
                context['orders'] = orders_data
                context['total_count'] = len(orders_data)
                context['has_next'] = False
                context['has_prev'] = False
            else:
                context['orders'] = []
                context['total_count'] = 0
                context['has_next'] = False
                context['has_prev'] = False
        else:
            context['orders'] = []
            context['total_count'] = 0
            context['has_next'] = False
            context['has_prev'] = False

        context['current_page'] = page
        context['total_pages'] = (context['total_count'] + limit - 1) // limit if context['total_count'] > 0 else 1

        return render(request, self.template_name, context)


class OrderDetailView(BaseView):
    """Buyurtma detallari"""
    template_name = 'frontend/account/order_detail.html'

    def get(self, request, pk):
        if 'access_token' not in request.session:
            return redirect('frontend:login')

        api = self.get_api_client(request)
        context = self.get_account_context(request)
        context['active_page'] = 'orders'

        order_response = api.get_order(pk)
        if order_response.get('error'):
            messages.error(request, 'Buyurtma topilmadi')
            return redirect('frontend:orders')

        context['order'] = order_response.get('data', {})

        return render(request, self.template_name, context)


class WishlistView(BaseView):
    """Wishlist sahifasi"""
    template_name = 'frontend/account/wishlist.html'

    def get(self, request):
        if 'access_token' not in request.session:
            return redirect('frontend:login')

        api = self.get_api_client(request)
        context = self.get_account_context(request)
        context['active_page'] = 'wishlist'

        wishlist_response = api.get_wishlist()
        if not wishlist_response.get('error'):
            wishlist_data = wishlist_response.get('data', {})
            if isinstance(wishlist_data, dict):
                context['wishlist'] = wishlist_data.get('results', [])
            elif isinstance(wishlist_data, list):
                context['wishlist'] = wishlist_data
            else:
                context['wishlist'] = []
        else:
            context['wishlist'] = []

        return render(request, self.template_name, context)


class WishlistAddView(BaseView):
    """Wishlistga qo'shish (AJAX)"""

    def post(self, request):
        if 'access_token' not in request.session:
            return JsonResponse({'error': True, 'message': 'Tizimga kiring'}, status=401)

        api = self.get_api_client(request)
        product_id = request.POST.get('product_id')

        if not product_id:
            return JsonResponse({'error': True, 'message': 'Mahsulot tanlanmadi'}, status=400)

        response = api.add_to_wishlist(product_id)

        if response.get('error'):
            return JsonResponse({
                'error': True,
                'message': response.get('message', 'Xatolik yuz berdi')
            }, status=response.get('status_code', 400))

        return JsonResponse({
            'error': False,
            'message': 'Wishlistga qo\'shildi',
            'data': response.get('data')
        })


class WishlistRemoveView(BaseView):
    """Wishlistdan o'chirish (AJAX)"""

    def post(self, request, pk):
        if 'access_token' not in request.session:
            return JsonResponse({'error': True, 'message': 'Tizimga kiring'}, status=401)

        api = self.get_api_client(request)
        response = api.remove_from_wishlist(pk)

        if response.get('error'):
            return JsonResponse({
                'error': True,
                'message': response.get('message', 'Xatolik yuz berdi')
            }, status=response.get('status_code', 400))

        return JsonResponse({
            'error': False,
            'message': 'O\'chirildi'
        })


class AddLocationView(BaseView):
    """Manzil qo'shish (AJAX)"""

    def post(self, request):
        if 'access_token' not in request.session:
            return JsonResponse({'error': True, 'message': 'Tizimga kiring'}, status=401)

        api = self.get_api_client(request)

        data = {
            'location': request.POST.get('location', ''),
            'latitude': request.POST.get('latitude', ''),
            'longitude': request.POST.get('longitude', ''),
            'floor': request.POST.get('floor', ''),
            'apartment': request.POST.get('apartment', ''),
        }

        response = api.add_location(data)

        if response.get('error'):
            return JsonResponse({
                'error': True,
                'message': response.get('message', 'Xatolik yuz berdi')
            }, status=response.get('status_code', 400))

        return JsonResponse({
            'error': False,
            'message': 'Manzil qo\'shildi',
            'data': response.get('data')
        })


class DeleteLocationView(BaseView):
    """Manzil o'chirish (AJAX)"""

    def post(self, request, pk):
        if 'access_token' not in request.session:
            return JsonResponse({'error': True, 'message': 'Tizimga kiring'}, status=401)

        api = self.get_api_client(request)
        response = api.delete_location(pk)

        if response.get('error'):
            return JsonResponse({
                'error': True,
                'message': response.get('message', 'Xatolik yuz berdi')
            }, status=response.get('status_code', 400))

        return JsonResponse({
            'error': False,
            'message': 'Manzil o\'chirildi'
        })


class CheckPromoView(BaseView):
    """Promo tekshirish (AJAX)"""

    def post(self, request):
        if 'access_token' not in request.session:
            return JsonResponse({'error': True, 'message': 'Tizimga kiring'}, status=401)

        api = self.get_api_client(request)
        promo_code = request.POST.get('promo', '')

        if not promo_code:
            return JsonResponse({'error': True, 'message': 'Promo kodni kiriting'}, status=400)

        response = api.check_promo(promo_code)

        if response.get('error'):
            return JsonResponse({
                'error': True,
                'message': response.get('message', 'Promo kod noto\'g\'ri')
            }, status=response.get('status_code', 400))

        return JsonResponse({
            'error': False,
            'message': 'Promo kod qabul qilindi',
            'data': response.get('data')
        })


class ChangePasswordView(BaseView):
    """Parolni o'zgartirish sahifasi"""
    template_name = 'frontend/account/change_password.html'

    def get(self, request):
        if 'access_token' not in request.session:
            return redirect('frontend:login')
        context = self.get_account_context(request)
        context['active_page'] = 'change_password'
        return render(request, self.template_name, context)

    def post(self, request):
        if 'access_token' not in request.session:
            return redirect('frontend:login')

        api = self.get_api_client(request)
        old_password = request.POST.get('old_password', '')
        new_password = request.POST.get('new_password', '')
        new_password_confirm = request.POST.get('new_password_confirm', '')

        if not all([old_password, new_password, new_password_confirm]):
            messages.error(request, 'Barcha maydonlarni to\'ldiring')
            context = self.get_account_context(request)
            context['active_page'] = 'change_password'
            return render(request, self.template_name, context)

        if new_password != new_password_confirm:
            messages.error(request, 'Yangi parollar mos kelmadi')
            context = self.get_account_context(request)
            context['active_page'] = 'change_password'
            return render(request, self.template_name, context)

        if len(new_password) < 8:
            messages.error(request, 'Parol kamida 8 ta belgidan iborat bo\'lishi kerak')
            context = self.get_account_context(request)
            context['active_page'] = 'change_password'
            return render(request, self.template_name, context)

        response = api.change_password(old_password, new_password, new_password_confirm)

        if response.get('error'):
            messages.error(request, response.get('message', 'Parolni o\'zgartirishda xatolik'))
            context = self.get_account_context(request)
            context['active_page'] = 'change_password'
            return render(request, self.template_name, context)

        messages.success(request, 'Parol muvaffaqiyatli o\'zgartirildi!')
        return redirect('frontend:profile')


class DeleteAccountView(BaseView):
    """Hisobni o'chirish (AJAX)"""

    def post(self, request):
        if 'access_token' not in request.session:
            return JsonResponse({'error': True, 'message': 'Tizimga kiring'}, status=401)

        api = self.get_api_client(request)
        password = request.POST.get('password', '')

        if not password:
            return JsonResponse({'error': True, 'message': 'Parolni kiriting'}, status=400)

        response = api.delete_account(password)

        if response.get('error'):
            return JsonResponse({
                'error': True,
                'message': response.get('message', 'Parol noto\'g\'ri')
            }, status=response.get('status_code', 400))

        # Session'ni tozalash
        request.session.flush()

        return JsonResponse({
            'error': False,
            'message': 'Hisobingiz o\'chirildi'
        })
