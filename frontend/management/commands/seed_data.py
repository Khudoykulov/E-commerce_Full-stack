"""
Bazani tozalash va to'g'ri demo ma'lumotlar bilan to'ldirish
"""
import os
import random
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class Command(BaseCommand):
    help = "Bazani tozalab, mos demo ma'lumotlar bilan to'ldirish"

    def add_arguments(self, parser):
        parser.add_argument(
            '--no-input',
            action='store_true',
            help="Tasdiqlashsiz bajarish",
        )

    def handle(self, *args, **options):
        if not options['no_input']:
            confirm = input(
                "\n⚠️  DIQQAT: Bazadagi BARCHA ma'lumotlar o'chiriladi!\n"
                "Davom etasizmi? (yes/no): "
            )
            if confirm.lower() not in ('yes', 'y', 'ha'):
                self.stdout.write(self.style.WARNING("Bekor qilindi."))
                return

        self.stdout.write(self.style.MIGRATE_HEADING("\n🗑️  Bazani tozalash..."))
        self._flush_database()

        self.stdout.write(self.style.MIGRATE_HEADING("\n📦 Ma'lumotlarni yaratish..."))
        self._create_superuser()
        users = self._create_users()
        locations = self._create_locations(users)
        self._create_call()
        self._create_advices()
        self._create_new_blocks()
        self._create_carta()
        categories = self._create_categories()
        products = self._create_products(categories)
        self._create_wishlists(users, products)
        self._create_likes(users, products)
        self._create_ranks(users, products)
        self._create_comments(users, products)
        cart_items = self._create_cart_items(users, products)
        self._create_promos(users)
        self._create_orders(users, locations, cart_items)

        self.stdout.write(self.style.SUCCESS("\n✅ Baza muvaffaqiyatli to'ldirildi!\n"))
        self._print_summary()

    def _flush_database(self):
        """Barcha ma'lumotlarni o'chirish"""
        from apps.order.models import Order, CartItem, Promo, Courier
        from apps.product.models import (
            Comment, CommentImage, Rank, Like, Wishlist,
            ProductImage, Product, Category, Tag
        )
        from apps.account.models import (
            UserToken, UserLocation, NewBlock, Advice, Call, Banner, Carta
        )

        # Tartib bilan o'chirish (FK bog'lanishlari uchun)
        Order.objects.all().delete()
        CartItem.objects.all().delete()
        Promo.objects.all().delete()
        Courier.objects.all().delete()
        Comment.objects.all().delete()
        CommentImage.objects.all().delete()
        Rank.objects.all().delete()
        Like.objects.all().delete()
        Wishlist.objects.all().delete()
        ProductImage.objects.all().delete()
        Product.objects.all().delete()
        Tag.objects.all().delete()
        Category.objects.all().delete()
        UserToken.objects.all().delete()
        UserLocation.objects.all().delete()
        NewBlock.objects.all().delete()
        Advice.objects.all().delete()
        Call.objects.all().delete()
        Banner.objects.all().delete()
        Carta.objects.all().delete()
        User.objects.all().delete()

        self.stdout.write("  ✓ Barcha jadvallar tozalandi")

    def _create_superuser(self):
        """Admin foydalanuvchi"""
        User.objects.create_superuser(
            phone='+998901234567',
            name='Admin',
            password='admin123',
        )
        self.stdout.write("  ✓ Superuser yaratildi: +998901234567 / admin123")

    def _create_users(self):
        """Demo foydalanuvchilar"""
        users_data = [
            {'phone': '+998901111111', 'name': 'Abdulloh Karimov'},
            {'phone': '+998902222222', 'name': 'Dilnoza Rahimova'},
            {'phone': '+998903333333', 'name': 'Jasur Toshmatov'},
            {'phone': '+998904444444', 'name': 'Malika Azimova'},
            {'phone': '+998905555555', 'name': 'Sardor Umarov'},
            {'phone': '+998906666666', 'name': 'Nodira Ergasheva'},
            {'phone': '+998907777777', 'name': 'Bekzod Aliyev'},
            {'phone': '+998908888888', 'name': 'Zulfiya Mirzayeva'},
        ]

        users = []
        for data in users_data:
            user = User.objects.create_user(
                phone=data['phone'],
                name=data['name'],
                password='user1234',
            )
            user.is_active = True
            user.save()
            users.append(user)

        self.stdout.write(f"  ✓ {len(users)} ta foydalanuvchi yaratildi (parol: user1234)")
        return users

    def _create_locations(self, users):
        """Foydalanuvchi manzillari"""
        from apps.account.models import UserLocation

        locations_data = [
            {'location': 'Toshkent, Chilonzor tumani, 9-kvartal, 15-uy', 'lat': '41.2856', 'lng': '69.2044', 'floor': '3', 'apt': '24'},
            {'location': 'Toshkent, Yunusobod tumani, 4-kvartal, 8-uy', 'lat': '41.3375', 'lng': '69.2846', 'floor': '5', 'apt': '12'},
            {'location': 'Toshkent, Mirzo Ulug\'bek tumani, Buyuk Ipak Yo\'li, 22', 'lat': '41.3410', 'lng': '69.3346', 'floor': '2', 'apt': '7'},
            {'location': 'Toshkent, Sergeli tumani, 7-kvartal, 3-uy', 'lat': '41.2260', 'lng': '69.2200', 'floor': '1', 'apt': '3'},
            {'location': 'Toshkent, Yakkasaroy tumani, Shota Rustaveli, 45', 'lat': '41.2950', 'lng': '69.2780', 'floor': '4', 'apt': '18'},
            {'location': 'Toshkent, Olmazor tumani, 14-kvartal, 11-uy', 'lat': '41.3280', 'lng': '69.2180', 'floor': '6', 'apt': '31'},
            {'location': 'Toshkent, Mirobod tumani, Amir Temur shox ko\'chasi, 100', 'lat': '41.3110', 'lng': '69.2790', 'floor': '8', 'apt': '42'},
            {'location': 'Toshkent, Shayxontohur tumani, Navoiy ko\'chasi, 12', 'lat': '41.3200', 'lng': '69.2500', 'floor': '2', 'apt': '9'},
        ]

        locations = []
        for i, user in enumerate(users):
            data = locations_data[i % len(locations_data)]
            loc = UserLocation.objects.create(
                user=user,
                location=data['location'],
                latitude=data['lat'],
                longitude=data['lng'],
                floor=data['floor'],
                apartment=data['apt'],
            )
            locations.append(loc)

        self.stdout.write(f"  ✓ {len(locations)} ta manzil yaratildi")
        return locations

    def _create_call(self):
        """Aloqa ma'lumotlari"""
        from apps.account.models import Call

        Call.objects.create(
            phone='+998901234567',
            telegram='https://t.me/wholesale_uz',
            instagram='https://instagram.com/wholesale_uz',
            tiktok='https://tiktok.com/@wholesale_uz',
            facebook='https://facebook.com/wholesale.uz',
        )
        self.stdout.write("  ✓ Aloqa ma'lumotlari yaratildi")

    def _create_advices(self):
        """Maslahatlar"""
        from apps.account.models import Advice

        advices = [
            {
                'title': 'Sifatli mahsulot tanlash',
                'title_uz': 'Sifatli mahsulot tanlash',
                'title_ru': 'Выбор качественного товара',
                'title_en': 'Choosing quality products',
                'description': 'Doimo sertifikatlangan mahsulotlarni tanlang',
                'description_uz': 'Doimo sertifikatlangan mahsulotlarni tanlang',
                'description_ru': 'Всегда выбирайте сертифицированные товары',
                'description_en': 'Always choose certified products',
            },
            {
                'title': 'Chegirmalardan foydalaning',
                'title_uz': 'Chegirmalardan foydalaning',
                'title_ru': 'Используйте скидки',
                'title_en': 'Take advantage of discounts',
                'description': 'Aksiya va chegirmalarni kuzatib boring',
                'description_uz': 'Aksiya va chegirmalarni kuzatib boring',
                'description_ru': 'Следите за акциями и скидками',
                'description_en': 'Keep track of promotions and discounts',
            },
            {
                'title': 'Ulgurji narxlar',
                'title_uz': 'Ulgurji narxlar',
                'title_ru': 'Оптовые цены',
                'title_en': 'Wholesale prices',
                'description': 'Ko\'proq xarid qilsangiz, narx pastroq bo\'ladi',
                'description_uz': 'Ko\'proq xarid qilsangiz, narx pastroq bo\'ladi',
                'description_ru': 'Чем больше покупаете, тем ниже цена',
                'description_en': 'The more you buy, the lower the price',
            },
        ]

        for data in advices:
            Advice.objects.create(**data)

        self.stdout.write(f"  ✓ {len(advices)} ta maslahat yaratildi")

    def _create_new_blocks(self):
        """Yangiliklar bloklari"""
        from apps.account.models import NewBlock

        blocks = [
            {
                'title': 'Yangi kolleksiya yetib keldi!',
                'title_uz': 'Yangi kolleksiya yetib keldi!',
                'title_ru': 'Новая коллекция прибыла!',
                'title_en': 'New collection has arrived!',
                'description': 'Eng so\'nggi trendlar va uslublar bizning do\'konimizda',
                'description_uz': 'Eng so\'nggi trendlar va uslublar bizning do\'konimizda',
                'description_ru': 'Последние тренды и стили в нашем магазине',
                'description_en': 'Latest trends and styles in our store',
            },
            {
                'title': 'Bepul yetkazib berish',
                'title_uz': 'Bepul yetkazib berish',
                'title_ru': 'Бесплатная доставка',
                'title_en': 'Free delivery',
                'description': '500 000 so\'mdan ortiq xaridlarda bepul yetkazib berish',
                'description_uz': '500 000 so\'mdan ortiq xaridlarda bepul yetkazib berish',
                'description_ru': 'Бесплатная доставка при покупке от 500 000 сум',
                'description_en': 'Free delivery for purchases over 500,000 UZS',
            },
        ]

        for data in blocks:
            NewBlock.objects.create(**data)

        self.stdout.write(f"  ✓ {len(blocks)} ta yangilik bloki yaratildi")

    def _create_carta(self):
        """Bank kartalari"""
        from apps.account.models import Carta

        cartas = [
            {
                'user_carta_name': 'Wholesale Do\'kon',
                'bank_name': 'Kapitalbank',
                'carta_number': '8600 1234 5678 9012',
                'bank_number': 1001,
            },
            {
                'user_carta_name': 'Wholesale Do\'kon',
                'bank_name': 'Uzcard',
                'carta_number': '8600 9876 5432 1098',
                'bank_number': 1002,
            },
        ]

        for data in cartas:
            Carta.objects.create(**data)

        self.stdout.write(f"  ✓ {len(cartas)} ta bank kartasi yaratildi")

    def _create_categories(self):
        """Kategoriyalar"""
        from apps.product.models import Category

        cats_data = [
            {
                'name': 'Elektronika',
                'name_uz': 'Elektronika',
                'name_ru': 'Электроника',
                'name_en': 'Electronics',
                'children': [
                    {'name': 'Smartfonlar', 'name_uz': 'Smartfonlar', 'name_ru': 'Смартфоны', 'name_en': 'Smartphones'},
                    {'name': 'Noutbuklar', 'name_uz': 'Noutbuklar', 'name_ru': 'Ноутбуки', 'name_en': 'Laptops'},
                    {'name': 'Quloqchinlar', 'name_uz': 'Quloqchinlar', 'name_ru': 'Наушники', 'name_en': 'Headphones'},
                ]
            },
            {
                'name': 'Kiyim-kechak',
                'name_uz': 'Kiyim-kechak',
                'name_ru': 'Одежда',
                'name_en': 'Clothing',
                'children': [
                    {'name': 'Erkaklar kiyimi', 'name_uz': 'Erkaklar kiyimi', 'name_ru': 'Мужская одежда', 'name_en': 'Men\'s clothing'},
                    {'name': 'Ayollar kiyimi', 'name_uz': 'Ayollar kiyimi', 'name_ru': 'Женская одежда', 'name_en': 'Women\'s clothing'},
                    {'name': 'Bolalar kiyimi', 'name_uz': 'Bolalar kiyimi', 'name_ru': 'Детская одежда', 'name_en': 'Children\'s clothing'},
                ]
            },
            {
                'name': 'Oziq-ovqat',
                'name_uz': 'Oziq-ovqat',
                'name_ru': 'Продукты питания',
                'name_en': 'Food',
                'children': [
                    {'name': 'Go\'sht mahsulotlari', 'name_uz': 'Go\'sht mahsulotlari', 'name_ru': 'Мясные продукты', 'name_en': 'Meat products'},
                    {'name': 'Sut mahsulotlari', 'name_uz': 'Sut mahsulotlari', 'name_ru': 'Молочные продукты', 'name_en': 'Dairy products'},
                    {'name': 'Ichimliklar', 'name_uz': 'Ichimliklar', 'name_ru': 'Напитки', 'name_en': 'Beverages'},
                ]
            },
            {
                'name': 'Uy-ro\'zg\'or',
                'name_uz': 'Uy-ro\'zg\'or',
                'name_ru': 'Товары для дома',
                'name_en': 'Home & Garden',
                'children': [
                    {'name': 'Oshxona jihozlari', 'name_uz': 'Oshxona jihozlari', 'name_ru': 'Кухонная техника', 'name_en': 'Kitchen appliances'},
                    {'name': 'Mebel', 'name_uz': 'Mebel', 'name_ru': 'Мебель', 'name_en': 'Furniture'},
                ]
            },
            {
                'name': 'Sport',
                'name_uz': 'Sport',
                'name_ru': 'Спорт',
                'name_en': 'Sports',
                'children': [
                    {'name': 'Sport kiyim', 'name_uz': 'Sport kiyim', 'name_ru': 'Спортивная одежда', 'name_en': 'Sportswear'},
                    {'name': 'Sport jihozlari', 'name_uz': 'Sport jihozlari', 'name_ru': 'Спортивное оборудование', 'name_en': 'Sports equipment'},
                ]
            },
            {
                'name': 'Salomatlik',
                'name_uz': 'Salomatlik',
                'name_ru': 'Здоровье',
                'name_en': 'Health',
                'children': []
            },
        ]

        categories = []
        for cat_data in cats_data:
            children = cat_data.pop('children')
            parent = Category.objects.create(**cat_data)
            categories.append(parent)
            for child_data in children:
                child = Category.objects.create(parent=parent, **child_data)
                categories.append(child)

        self.stdout.write(f"  ✓ {len(categories)} ta kategoriya yaratildi")
        return categories

    def _create_products(self, categories):
        """Mahsulotlar"""
        from apps.product.models import Product, Category

        # Subkategoriyalar bilan ishlash — faqat bolalari bor kategoryalar
        sub_categories = Category.objects.filter(parent__isnull=False)

        products_data = {
            'Smartfonlar': [
                {'name': 'Samsung Galaxy S24 Ultra', 'name_uz': 'Samsung Galaxy S24 Ultra', 'name_ru': 'Samsung Galaxy S24 Ultra', 'name_en': 'Samsung Galaxy S24 Ultra', 'price': 15500000, 'discount': 5, 'quantity': 25, 'description': 'Eng yangi Samsung flagman smartfoni', 'description_uz': 'Eng yangi Samsung flagman smartfoni', 'description_ru': 'Новейший флагман Samsung', 'description_en': 'Latest Samsung flagship smartphone', 'sold_count': 120, 'views': 3500},
                {'name': 'iPhone 15 Pro Max', 'name_uz': 'iPhone 15 Pro Max', 'name_ru': 'iPhone 15 Pro Max', 'name_en': 'iPhone 15 Pro Max', 'price': 18000000, 'discount': 0, 'quantity': 15, 'description': 'Apple kompaniyasining eng yuqori darajadagi smartfoni', 'description_uz': 'Apple kompaniyasining eng yuqori darajadagi smartfoni', 'description_ru': 'Топовый смартфон от Apple', 'description_en': 'Apple\'s top-tier smartphone', 'sold_count': 200, 'views': 5200},
                {'name': 'Xiaomi 14 Pro', 'name_uz': 'Xiaomi 14 Pro', 'name_ru': 'Xiaomi 14 Pro', 'name_en': 'Xiaomi 14 Pro', 'price': 7200000, 'discount': 10, 'quantity': 40, 'description': 'Sifatli va arzon narxdagi smartfon', 'description_uz': 'Sifatli va arzon narxdagi smartfon', 'description_ru': 'Качественный и доступный смартфон', 'description_en': 'Quality affordable smartphone', 'sold_count': 85, 'views': 2100},
            ],
            'Noutbuklar': [
                {'name': 'MacBook Air M3', 'name_uz': 'MacBook Air M3', 'name_ru': 'MacBook Air M3', 'name_en': 'MacBook Air M3', 'price': 22000000, 'discount': 3, 'quantity': 10, 'description': 'Eng yengil va kuchli noutbuk', 'description_uz': 'Eng yengil va kuchli noutbuk', 'description_ru': 'Самый легкий и мощный ноутбук', 'description_en': 'Lightest and most powerful laptop', 'sold_count': 45, 'views': 1800},
                {'name': 'Lenovo ThinkPad X1 Carbon', 'name_uz': 'Lenovo ThinkPad X1 Carbon', 'name_ru': 'Lenovo ThinkPad X1 Carbon', 'name_en': 'Lenovo ThinkPad X1 Carbon', 'price': 16500000, 'discount': 7, 'quantity': 8, 'description': 'Biznes uchun mo\'ljallangan professional noutbuk', 'description_uz': 'Biznes uchun mo\'ljallangan professional noutbuk', 'description_ru': 'Профессиональный ноутбук для бизнеса', 'description_en': 'Professional business laptop', 'sold_count': 30, 'views': 900},
            ],
            'Quloqchinlar': [
                {'name': 'AirPods Pro 2', 'name_uz': 'AirPods Pro 2', 'name_ru': 'AirPods Pro 2', 'name_en': 'AirPods Pro 2', 'price': 3500000, 'discount': 0, 'quantity': 50, 'description': 'Eng yaxshi shovqin bekor qiluvchi quloqchin', 'description_uz': 'Eng yaxshi shovqin bekor qiluvchi quloqchin', 'description_ru': 'Лучшие наушники с шумоподавлением', 'description_en': 'Best noise cancelling earbuds', 'sold_count': 150, 'views': 4000},
                {'name': 'Sony WH-1000XM5', 'name_uz': 'Sony WH-1000XM5', 'name_ru': 'Sony WH-1000XM5', 'name_en': 'Sony WH-1000XM5', 'price': 4800000, 'discount': 15, 'quantity': 20, 'description': 'Premium simsiz quloqchin', 'description_uz': 'Premium simsiz quloqchin', 'description_ru': 'Премиум беспроводные наушники', 'description_en': 'Premium wireless headphones', 'sold_count': 65, 'views': 1500},
            ],
            'Erkaklar kiyimi': [
                {'name': 'Klassik kostyum (3 qismli)', 'name_uz': 'Klassik kostyum (3 qismli)', 'name_ru': 'Классический костюм (3 части)', 'name_en': 'Classic 3-piece suit', 'price': 2800000, 'discount': 20, 'quantity': 30, 'description': 'Yuqori sifatli erkaklar kostymi', 'description_uz': 'Yuqori sifatli erkaklar kostymi', 'description_ru': 'Высококачественный мужской костюм', 'description_en': 'High quality men\'s suit', 'sold_count': 40, 'views': 800},
                {'name': 'Polo ko\'ylak', 'name_uz': 'Polo ko\'ylak', 'name_ru': 'Поло рубашка', 'name_en': 'Polo shirt', 'price': 350000, 'discount': 0, 'quantity': 100, 'description': 'Paxta polo ko\'ylak', 'description_uz': 'Paxta polo ko\'ylak', 'description_ru': 'Хлопковая рубашка-поло', 'description_en': 'Cotton polo shirt', 'sold_count': 200, 'views': 3000},
            ],
            'Ayollar kiyimi': [
                {'name': 'Yozgi ko\'ylak', 'name_uz': 'Yozgi ko\'ylak', 'name_ru': 'Летнее платье', 'name_en': 'Summer dress', 'price': 450000, 'discount': 25, 'quantity': 60, 'description': 'Yengil va qulay yozgi ko\'ylak', 'description_uz': 'Yengil va qulay yozgi ko\'ylak', 'description_ru': 'Легкое и удобное летнее платье', 'description_en': 'Light and comfortable summer dress', 'sold_count': 90, 'views': 2500},
                {'name': 'Jins shimlar', 'name_uz': 'Jins shimlar', 'name_ru': 'Джинсы', 'name_en': 'Jeans', 'price': 550000, 'discount': 10, 'quantity': 80, 'description': 'Klassik ayollar jins shimlari', 'description_uz': 'Klassik ayollar jins shimlari', 'description_ru': 'Классические женские джинсы', 'description_en': 'Classic women\'s jeans', 'sold_count': 110, 'views': 1800},
            ],
            'Bolalar kiyimi': [
                {'name': 'Bolalar sport kostymi', 'name_uz': 'Bolalar sport kostymi', 'name_ru': 'Детский спортивный костюм', 'name_en': 'Children\'s tracksuit', 'price': 280000, 'discount': 15, 'quantity': 70, 'description': '3-12 yosh uchun sport kostym', 'description_uz': '3-12 yosh uchun sport kostym', 'description_ru': 'Спортивный костюм для детей 3-12 лет', 'description_en': 'Tracksuit for children aged 3-12', 'sold_count': 60, 'views': 1200},
            ],
            'Go\'sht mahsulotlari': [
                {'name': 'Mol go\'shti (1 kg)', 'name_uz': 'Mol go\'shti (1 kg)', 'name_ru': 'Говядина (1 кг)', 'name_en': 'Beef (1 kg)', 'price': 120000, 'discount': 0, 'quantity': 200, 'description': 'Yangi mol go\'shti', 'description_uz': 'Yangi mol go\'shti', 'description_ru': 'Свежая говядина', 'description_en': 'Fresh beef', 'sold_count': 500, 'views': 6000},
                {'name': 'Tovuq filesi (1 kg)', 'name_uz': 'Tovuq filesi (1 kg)', 'name_ru': 'Куриное филе (1 кг)', 'name_en': 'Chicken fillet (1 kg)', 'price': 45000, 'discount': 5, 'quantity': 300, 'description': 'Yangi tovuq go\'shti', 'description_uz': 'Yangi tovuq go\'shti', 'description_ru': 'Свежее куриное мясо', 'description_en': 'Fresh chicken meat', 'sold_count': 800, 'views': 7500},
            ],
            'Sut mahsulotlari': [
                {'name': 'Sut (1 litr)', 'name_uz': 'Sut (1 litr)', 'name_ru': 'Молоко (1 литр)', 'name_en': 'Milk (1 liter)', 'price': 12000, 'discount': 0, 'quantity': 500, 'description': 'Tabiiy sigir suti', 'description_uz': 'Tabiiy sigir suti', 'description_ru': 'Натуральное коровье молоко', 'description_en': 'Natural cow milk', 'sold_count': 1200, 'views': 9000},
                {'name': 'Qatiq (0.5 litr)', 'name_uz': 'Qatiq (0.5 litr)', 'name_ru': 'Кефир (0.5 литра)', 'name_en': 'Yogurt (0.5 liter)', 'price': 8000, 'discount': 0, 'quantity': 400, 'description': 'An\'anaviy qatiq', 'description_uz': 'An\'anaviy qatiq', 'description_ru': 'Традиционный кефир', 'description_en': 'Traditional yogurt', 'sold_count': 900, 'views': 5000},
            ],
            'Ichimliklar': [
                {'name': 'Coca-Cola (1.5 litr)', 'name_uz': 'Coca-Cola (1.5 litr)', 'name_ru': 'Coca-Cola (1.5 литра)', 'name_en': 'Coca-Cola (1.5 liter)', 'price': 15000, 'discount': 0, 'quantity': 1000, 'description': 'Gazli ichimlik', 'description_uz': 'Gazli ichimlik', 'description_ru': 'Газированный напиток', 'description_en': 'Carbonated drink', 'sold_count': 2000, 'views': 12000},
                {'name': 'Choy (100g)', 'name_uz': 'Choy (100g)', 'name_ru': 'Чай (100г)', 'name_en': 'Tea (100g)', 'price': 25000, 'discount': 10, 'quantity': 300, 'description': 'Yuqori sifatli ko\'k choy', 'description_uz': 'Yuqori sifatli ko\'k choy', 'description_ru': 'Высококачественный зеленый чай', 'description_en': 'High quality green tea', 'sold_count': 700, 'views': 4500},
            ],
            'Oshxona jihozlari': [
                {'name': 'Blender Philips', 'name_uz': 'Blender Philips', 'name_ru': 'Блендер Philips', 'name_en': 'Blender Philips', 'price': 850000, 'discount': 12, 'quantity': 35, 'description': 'Ko\'p funksiyali blender', 'description_uz': 'Ko\'p funksiyali blender', 'description_ru': 'Многофункциональный блендер', 'description_en': 'Multi-functional blender', 'sold_count': 55, 'views': 1600},
                {'name': 'Elektr choynak', 'name_uz': 'Elektr choynak', 'name_ru': 'Электрический чайник', 'name_en': 'Electric kettle', 'price': 350000, 'discount': 0, 'quantity': 45, 'description': 'Tez qaynaydigan choynak (2L)', 'description_uz': 'Tez qaynaydigan choynak (2L)', 'description_ru': 'Быстрокипящий чайник (2л)', 'description_en': 'Fast boiling kettle (2L)', 'sold_count': 80, 'views': 2200},
            ],
            'Mebel': [
                {'name': 'Ofis stuli', 'name_uz': 'Ofis stuli', 'name_ru': 'Офисный стул', 'name_en': 'Office chair', 'price': 1500000, 'discount': 8, 'quantity': 20, 'description': 'Ergonomik ofis stuli', 'description_uz': 'Ergonomik ofis stuli', 'description_ru': 'Эргономичное офисное кресло', 'description_en': 'Ergonomic office chair', 'sold_count': 25, 'views': 700},
            ],
            'Sport kiyim': [
                {'name': 'Nike sport krossovka', 'name_uz': 'Nike sport krossovka', 'name_ru': 'Кроссовки Nike', 'name_en': 'Nike sneakers', 'price': 1200000, 'discount': 15, 'quantity': 40, 'description': 'Original Nike sport poyabzal', 'description_uz': 'Original Nike sport poyabzal', 'description_ru': 'Оригинальные кроссовки Nike', 'description_en': 'Original Nike sports shoes', 'sold_count': 75, 'views': 3200},
                {'name': 'Adidas futbolka', 'name_uz': 'Adidas futbolka', 'name_ru': 'Футболка Adidas', 'name_en': 'Adidas T-shirt', 'price': 250000, 'discount': 0, 'quantity': 90, 'description': 'Sport uchun qulay futbolka', 'description_uz': 'Sport uchun qulay futbolka', 'description_ru': 'Удобная спортивная футболка', 'description_en': 'Comfortable sports T-shirt', 'sold_count': 130, 'views': 2800},
            ],
            'Sport jihozlari': [
                {'name': 'Gantellar to\'plami (20 kg)', 'name_uz': 'Gantellar to\'plami (20 kg)', 'name_ru': 'Набор гантелей (20 кг)', 'name_en': 'Dumbbell set (20 kg)', 'price': 800000, 'discount': 5, 'quantity': 15, 'description': 'Uy mashqlari uchun gantellar', 'description_uz': 'Uy mashqlari uchun gantellar', 'description_ru': 'Гантели для домашних тренировок', 'description_en': 'Dumbbells for home workouts', 'sold_count': 35, 'views': 1100},
            ],
            'Salomatlik': [
                {'name': 'Vitamin C (60 tabletka)', 'name_uz': 'Vitamin C (60 tabletka)', 'name_ru': 'Витамин С (60 таблеток)', 'name_en': 'Vitamin C (60 tablets)', 'price': 85000, 'discount': 0, 'quantity': 150, 'description': 'Immunitetni kuchaytiruvchi vitamin', 'description_uz': 'Immunitetni kuchaytiruvchi vitamin', 'description_ru': 'Витамин для укрепления иммунитета', 'description_en': 'Immunity boosting vitamin', 'sold_count': 300, 'views': 4000},
                {'name': 'Tibbiy niqob (50 dona)', 'name_uz': 'Tibbiy niqob (50 dona)', 'name_ru': 'Медицинские маски (50 шт)', 'name_en': 'Medical masks (50 pcs)', 'price': 35000, 'discount': 0, 'quantity': 500, 'description': 'Bir martalik tibbiy niqoblar', 'description_uz': 'Bir martalik tibbiy niqoblar', 'description_ru': 'Одноразовые медицинские маски', 'description_en': 'Disposable medical masks', 'sold_count': 1500, 'views': 8000},
            ],
        }

        all_products = []
        for cat_name, prods in products_data.items():
            try:
                category = Category.objects.get(name_uz=cat_name)
            except Category.DoesNotExist:
                # Parent nomi bo'yicha qidirish
                category = Category.objects.filter(name=cat_name).first()
                if not category:
                    continue

            for prod_data in prods:
                prod_data['category'] = category
                prod_data['price'] = Decimal(str(prod_data['price']))
                product = Product.objects.create(**prod_data)
                all_products.append(product)

        self.stdout.write(f"  ✓ {len(all_products)} ta mahsulot yaratildi")
        return all_products

    def _create_wishlists(self, users, products):
        """Sevimlilar"""
        from apps.product.models import Wishlist

        count = 0
        for user in users[:5]:
            chosen = random.sample(products, min(3, len(products)))
            for product in chosen:
                Wishlist.objects.create(user=user, product=product)
                count += 1

        self.stdout.write(f"  ✓ {count} ta sevimli yaratildi")

    def _create_likes(self, users, products):
        """Yoqtirishlar"""
        from apps.product.models import Like

        count = 0
        for user in users:
            chosen = random.sample(products, min(5, len(products)))
            for product in chosen:
                Like.objects.create(user=user, product=product)
                count += 1

        self.stdout.write(f"  ✓ {count} ta like yaratildi")

    def _create_ranks(self, users, products):
        """Baholar"""
        from apps.product.models import Rank

        count = 0
        for user in users[:6]:
            chosen = random.sample(products, min(4, len(products)))
            for product in chosen:
                Rank.objects.create(
                    user=user,
                    product=product,
                    rank=random.randint(3, 10),
                )
                count += 1

        self.stdout.write(f"  ✓ {count} ta baho yaratildi")

    def _create_comments(self, users, products):
        """Izohlar"""
        from apps.product.models import Comment

        comments_texts = [
            'Juda yaxshi mahsulot, tavsiya qilaman!',
            'Sifati zo\'r, narxi ham arzon.',
            'Tez yetkazib berishdi, rahmat!',
            'Kutganimdan yaxshiroq chiqdi.',
            'Ishlatib ko\'rdim, juda mamnunman.',
            'Normalni mahsulot, o\'rtacha sifat.',
            'Do\'stlarimga ham tavsiya qildim.',
            'Ikkinchi marta buyurtma qilyapman.',
        ]

        count = 0
        for product in random.sample(products, min(10, len(products))):
            # 1-2 ta root comment
            for _ in range(random.randint(1, 2)):
                user = random.choice(users)
                comment = Comment.objects.create(
                    product=product,
                    user=user,
                    comment=random.choice(comments_texts),
                )
                count += 1

                # Ba'zi commentlarga javob
                if random.random() > 0.5:
                    reply_user = random.choice(users)
                    Comment.objects.create(
                        product=product,
                        user=reply_user,
                        parent=comment,
                        comment=random.choice([
                            'Qo\'shilaman!',
                            'Men ham xuddi shunday fikrdaman.',
                            'Rahmat fikringiz uchun!',
                            'Qayerdan sotib oldingiz?',
                        ]),
                    )
                    count += 1

        self.stdout.write(f"  ✓ {count} ta izoh yaratildi")

    def _create_cart_items(self, users, products):
        """Savatcha elementlari"""
        from apps.order.models import CartItem

        all_items = []
        # Har bir userga 1-3 ta savatcha element
        for user in users[:5]:
            chosen = random.sample(products, min(random.randint(1, 3), len(products)))
            for product in chosen:
                item = CartItem.objects.create(
                    user=user,
                    product=product,
                    quantity=random.randint(1, 5),
                )
                all_items.append(item)

        self.stdout.write(f"  ✓ {len(all_items)} ta savatcha elementi yaratildi")
        return all_items

    def _create_promos(self, users):
        """Promo kodlar"""
        from apps.order.models import Promo

        admin = User.objects.filter(is_superuser=True).first()

        promos = [
            {'name': 'YANGI10', 'discount': 10, 'min_price': Decimal('100000.00'), 'description': 'Yangi foydalanuvchilar uchun 10% chegirma'},
            {'name': 'YOZ2025', 'discount': 15, 'min_price': Decimal('200000.00'), 'description': 'Yozgi aksiya - 15% chegirma'},
            {'name': 'VIP20', 'discount': 20, 'min_price': Decimal('500000.00'), 'description': 'VIP mijozlar uchun 20% chegirma'},
        ]

        for promo_data in promos:
            Promo.objects.create(user=admin, **promo_data)

        self.stdout.write(f"  ✓ {len(promos)} ta promo kod yaratildi")

    def _create_orders(self, users, locations, cart_items):
        """Buyurtmalar"""
        from apps.order.models import Order, CartItem

        statuses = ['preparing', 'out_for_delivery', 'delivered']
        count = 0

        # Har bir foydalanuvchi uchun 1-2 ta buyurtma
        for i, user in enumerate(users[:5]):
            location = locations[i] if i < len(locations) else locations[0]

            # Yangi cart item yaratish (buyurtma uchun alohida)
            user_products = random.sample(
                list(range(len(cart_items))),
                min(random.randint(1, 3), len(cart_items))
            )

            for j in range(random.randint(1, 2)):
                status = random.choice(statuses)

                # Buyurtma uchun alohida CartItem
                order_items = []
                items_data = []
                for idx in random.sample(user_products, min(random.randint(1, 2), len(user_products))):
                    src_item = cart_items[idx]
                    item = CartItem.objects.create(
                        user=user,
                        product=src_item.product,
                        quantity=random.randint(1, 3),
                    )
                    order_items.append(item)
                    items_data.append({
                        'product_id': src_item.product.id,
                        'product_name': src_item.product.name,
                        'product_image': '',
                        'quantity': item.quantity,
                        'price': str(item.get_amount),
                    })

                order = Order(
                    user=user,
                    location=location,
                    status=status,
                    items_data=items_data,
                )

                if status == 'delivered':
                    order.payment_confirmed = True
                elif status == 'out_for_delivery':
                    order.payment_confirmed = random.choice([True, None])

                order.save()

                for item in order_items:
                    order.items.add(item)

                count += 1

        self.stdout.write(f"  ✓ {count} ta buyurtma yaratildi")

    def _print_summary(self):
        """Yakuniy hisobot"""
        from apps.product.models import Product, Category, Wishlist, Like, Rank, Comment
        from apps.order.models import Order, CartItem, Promo
        from apps.account.models import UserLocation, Advice, Call, NewBlock, Carta

        self.stdout.write(self.style.MIGRATE_HEADING("\n📊 YAKUNIY HISOBOT:"))
        self.stdout.write(f"  👤 Foydalanuvchilar:  {User.objects.count()}")
        self.stdout.write(f"  📍 Manzillar:         {UserLocation.objects.count()}")
        self.stdout.write(f"  📂 Kategoriyalar:     {Category.objects.count()}")
        self.stdout.write(f"  📦 Mahsulotlar:       {Product.objects.count()}")
        self.stdout.write(f"  ❤️  Wishlist:          {Wishlist.objects.count()}")
        self.stdout.write(f"  👍 Like:              {Like.objects.count()}")
        self.stdout.write(f"  ⭐ Baholar:           {Rank.objects.count()}")
        self.stdout.write(f"  💬 Izohlar:           {Comment.objects.count()}")
        self.stdout.write(f"  🛒 Savatcha:          {CartItem.objects.count()}")
        self.stdout.write(f"  📋 Buyurtmalar:       {Order.objects.count()}")
        self.stdout.write(f"  🎫 Promo kodlar:      {Promo.objects.count()}")
        self.stdout.write(f"  📰 Maslahatlar:       {Advice.objects.count()}")
        self.stdout.write(f"  💳 Bank kartalari:    {Carta.objects.count()}")
        self.stdout.write(f"  📞 Aloqa:             {Call.objects.count()}")
        self.stdout.write(f"  📰 Yangiliklar:       {NewBlock.objects.count()}")
        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("  🔑 Admin: +998901234567 / admin123"))
        self.stdout.write(self.style.SUCCESS("  🔑 User:  +998901111111 / user1234"))
        self.stdout.write("")
