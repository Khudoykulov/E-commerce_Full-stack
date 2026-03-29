"""
API Client - DRF endpointlar bilan ishlash uchun
"""
import requests
from django.conf import settings


class APIClient:
    """Backend API bilan ishlash uchun client"""

    def __init__(self, request=None):
        self.base_url = self._get_base_url(request)
        self.token = None
        self.language = 'uz'

        if request:
            self.token = request.session.get('access_token')
            self.language = request.LANGUAGE_CODE or 'uz'

    def _get_base_url(self, request):
        """Request asosida base URL ni aniqlash"""
        if request:
            scheme = 'https' if request.is_secure() else 'http'
            return f"{scheme}://{request.get_host()}"
        return "http://127.0.0.1:8000"

    def _fix_image_urls(self, data):
        """Rasm URL'larini to'liq URL ga o'zgartirish"""
        if isinstance(data, dict):
            for key, value in data.items():
                if key in ('image', 'avatar', 'product_image') and value:
                    if isinstance(value, str) and not value.startswith('http'):
                        if value.startswith('/'):
                            data[key] = self.base_url + value
                        else:
                            data[key] = self.base_url + '/' + value
                elif key == 'images' and isinstance(value, list):
                    for img in value:
                        if isinstance(img, dict) and 'image' in img:
                            if img['image'] and not img['image'].startswith('http'):
                                if img['image'].startswith('/'):
                                    img['image'] = self.base_url + img['image']
                                else:
                                    img['image'] = self.base_url + '/' + img['image']
                elif isinstance(value, dict):
                    self._fix_image_urls(value)
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, dict):
                            self._fix_image_urls(item)
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    self._fix_image_urls(item)
        return data

    def _get_headers(self, include_auth=True):
        """Request headerlarini tayyorlash"""
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Accept-Language': self.language,
        }
        if include_auth and self.token:
            headers['Authorization'] = f'Bearer {self.token}'
        return headers

    def _get_headers_multipart(self):
        """Multipart request uchun headerlar"""
        headers = {
            'Accept': 'application/json',
            'Accept-Language': self.language,
        }
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'
        return headers

    def get(self, endpoint, params=None):
        """GET request"""
        try:
            url = f"{self.base_url}{endpoint}"
            response = requests.get(url, headers=self._get_headers(), params=params, timeout=10)
            # Agar token eskirgan bo'lsa, public endpointlar uchun authsiz qayta urinib ko'ramiz.
            if response.status_code == 401 and self.token:
                response = requests.get(url, headers=self._get_headers(include_auth=False), params=params, timeout=10)
            return self._handle_response(response)
        except requests.exceptions.RequestException as e:
            return {'error': True, 'message': str(e), 'status_code': 500}

    def post(self, endpoint, data=None, files=None):
        """POST request"""
        try:
            url = f"{self.base_url}{endpoint}"
            if files:
                headers = self._get_headers_multipart()
                response = requests.post(url, headers=headers, data=data, files=files, timeout=10)
            else:
                response = requests.post(url, headers=self._get_headers(), json=data, timeout=10)
            return self._handle_response(response)
        except requests.exceptions.RequestException as e:
            return {'error': True, 'message': str(e), 'status_code': 500}

    def put(self, endpoint, data=None, files=None):
        """PUT request"""
        try:
            url = f"{self.base_url}{endpoint}"
            if files:
                headers = self._get_headers_multipart()
                response = requests.put(url, headers=headers, data=data, files=files, timeout=10)
            else:
                response = requests.put(url, headers=self._get_headers(), json=data, timeout=10)
            return self._handle_response(response)
        except requests.exceptions.RequestException as e:
            return {'error': True, 'message': str(e), 'status_code': 500}

    def patch(self, endpoint, data=None):
        """PATCH request"""
        try:
            url = f"{self.base_url}{endpoint}"
            response = requests.patch(url, headers=self._get_headers(), json=data, timeout=10)
            return self._handle_response(response)
        except requests.exceptions.RequestException as e:
            return {'error': True, 'message': str(e), 'status_code': 500}

    def delete(self, endpoint):
        """DELETE request"""
        try:
            url = f"{self.base_url}{endpoint}"
            response = requests.delete(url, headers=self._get_headers(), timeout=10)
            return self._handle_response(response)
        except requests.exceptions.RequestException as e:
            return {'error': True, 'message': str(e), 'status_code': 500}

    def _handle_response(self, response):
        """Response ni qayta ishlash"""
        result = {
            'status_code': response.status_code,
            'error': response.status_code >= 400,
        }

        try:
            result['data'] = response.json()
        except ValueError:
            result['data'] = None
            result['message'] = response.text

        # Rasm URL'larini to'liq URL ga o'zgartirish (try blokidan tashqarida)
        if result['data']:
            try:
                self._fix_image_urls(result['data'])
            except Exception:
                pass  # URL fix xatosi bo'lsa ham davom etamiz

        if result['error']:
            if isinstance(result.get('data'), dict):
                result['message'] = result['data'].get('detail', str(result['data']))
            else:
                result['message'] = 'Xatolik yuz berdi'

        return result

    # === Account API ===
    def login(self, phone, password):
        """Foydalanuvchi login"""
        return self.post('/api/account/login/', {'phone': phone, 'password': password})

    def register(self, name, phone, password1, password2):
        """Ro'yxatdan o'tish"""
        return self.post('/api/account/register/', {
            'name': name,
            'phone': phone,
            'password1': password1,
            'password2': password2
        })

    def get_profile(self):
        """Profil olish"""
        return self.get('/api/account/profile/')

    def update_profile(self, data, avatar=None):
        """Profil yangilash"""
        if avatar:
            return self.put('/api/account/profile/', data, files={'avatar': avatar})
        return self.patch('/api/account/profile/', data)

    def get_locations(self):
        """User manzillari"""
        return self.get('/api/account/location/')

    def add_location(self, data):
        """Manzil qo'shish"""
        return self.post('/api/account/location/', data)

    def delete_location(self, location_id):
        """Manzil o'chirish"""
        return self.delete(f'/api/account/location/{location_id}/')

    def get_banners(self):
        """Bannerlar"""
        return self.get('/api/account/banners/')

    # === Product API ===
    def get_categories(self, search=None):
        """Kategoriyalar"""
        params = {}
        if search:
            params['search'] = search
        return self.get('/api/product/categories/', params)

    def get_category(self, category_id):
        """Kategoriya detallari"""
        return self.get(f'/api/product/categories/{category_id}/')

    def get_products(self, search=None, category=None, ordering=None, limit=12, offset=0):
        """Mahsulotlar ro'yxati"""
        params = {'limit': limit, 'offset': offset}
        if search:
            params['search'] = search
        if category:
            params['category'] = category
        if ordering:
            params['ordering'] = ordering
        return self.get('/api/product/', params)

    def get_product(self, product_id):
        """Mahsulot detallari"""
        return self.get(f'/api/product/{product_id}/')

    def get_best_selling(self, limit=12, offset=0):
        """Eng ko'p sotilganlar"""
        return self.get('/api/product/best-selling/', {'limit': limit, 'offset': offset})

    def get_newly_added(self, limit=12, offset=0):
        """Yangi mahsulotlar"""
        return self.get('/api/product/newly-added/', {'limit': limit, 'offset': offset})

    def get_wishlist(self):
        """Wishlist"""
        return self.get('/api/product/wishlists/')

    def add_to_wishlist(self, product_id):
        """Wishlistga qo'shish"""
        return self.post('/api/product/wishlists/', {'product': product_id})

    def remove_from_wishlist(self, wishlist_id):
        """Wishlistdan o'chirish"""
        return self.delete(f'/api/product/wishlists/{wishlist_id}/')

    # === Cart API ===
    def get_cart(self):
        """Savatcha"""
        return self.get('/api/order/cart-items/')

    def add_to_cart(self, product_id, quantity=1):
        """Savatchaga qo'shish"""
        return self.post('/api/order/cart-items/', {'product': product_id, 'quantity': quantity})

    def update_cart_item(self, item_id, quantity):
        """Savatcha itemni yangilash"""
        return self.patch(f'/api/order/cart-items/{item_id}/', {'quantity': quantity})

    def remove_from_cart(self, item_id):
        """Savatchadan o'chirish"""
        return self.delete(f'/api/order/cart-items/{item_id}/')

    def clear_cart(self):
        """Savatchani tozalash"""
        return self.delete('/api/order/cart-items/clear-cart/')

    # === Order API ===
    def get_orders(self, limit=20, offset=0):
        """Buyurtmalar"""
        return self.get('/api/order/', {'limit': limit, 'offset': offset})

    def get_order(self, order_id):
        """Buyurtma detallari"""
        return self.get(f'/api/order/{order_id}/')

    def create_order(self, items, location_id, promo=None, file=None):
        """Buyurtma yaratish"""
        data = {
            'items': ','.join(map(str, items)),
            'location': location_id,
        }
        if promo:
            data['promo'] = promo
        if file:
            return self.post('/api/order/', data, files={'file': file})
        return self.post('/api/order/', data)

    def check_promo(self, promo_code):
        """Promo tekshirish"""
        return self.post('/api/order/check_promo/', {'name': promo_code})

    def change_password(self, old_password, new_password, new_password_confirm):
        """Parolni o'zgartirish"""
        return self.post('/api/account/profile/password/change/', {
            'old_password': old_password,
            'new_password': new_password,
            'new_password_confirm': new_password_confirm
        })

    def delete_account(self, password):
        """Hisobni o'chirish"""
        return self.post('/api/account/profile/delete/', {
            'password': password
        })
