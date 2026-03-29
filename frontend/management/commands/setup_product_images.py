"""
Mahsulotlarga mos rasmlarni yuklab qo'shish
"""
import os
import requests
from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.files.base import ContentFile
from apps.product.models import Product, ProductImage, Category


class Command(BaseCommand):
    help = 'Mahsulotlarga internet orqali mos rasmlarni yuklab qo\'shish'

    # Kategoriya va mahsulotlarga mos rasm URL lari (Unsplash/Pexels dan bepul rasmlar)
    CATEGORY_IMAGES = {
        'elektronika': 'https://images.unsplash.com/photo-1498049794561-7780e7231661?w=400&h=400&fit=crop',
        'electronics': 'https://images.unsplash.com/photo-1498049794561-7780e7231661?w=400&h=400&fit=crop',
        'oziq-ovqat': 'https://images.unsplash.com/photo-1543168256-418811576931?w=400&h=400&fit=crop',
        'food': 'https://images.unsplash.com/photo-1543168256-418811576931?w=400&h=400&fit=crop',
        'kiyim': 'https://images.unsplash.com/photo-1489987707025-afc232f7ea0f?w=400&h=400&fit=crop',
        'clothes': 'https://images.unsplash.com/photo-1489987707025-afc232f7ea0f?w=400&h=400&fit=crop',
        'sport': 'https://images.unsplash.com/photo-1517836357463-d25dfeac3438?w=400&h=400&fit=crop',
        'uy-jihozlari': 'https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=400&h=400&fit=crop',
        'furniture': 'https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=400&h=400&fit=crop',
        'mebel': 'https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=400&h=400&fit=crop',
        'default': 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=400&h=400&fit=crop',
    }

    PRODUCT_IMAGES = {
        # Elektronika
        'telefon': 'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=400&h=400&fit=crop',
        'phone': 'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=400&h=400&fit=crop',
        'smartphone': 'https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=400&h=400&fit=crop',
        'iphone': 'https://images.unsplash.com/photo-1592750475338-74b7b21085ab?w=400&h=400&fit=crop',
        'samsung': 'https://images.unsplash.com/photo-1610945265064-0e34e5519bbf?w=400&h=400&fit=crop',
        'laptop': 'https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=400&h=400&fit=crop',
        'noutbuk': 'https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=400&h=400&fit=crop',
        'kompyuter': 'https://images.unsplash.com/photo-1587831990711-23ca6441447b?w=400&h=400&fit=crop',
        'computer': 'https://images.unsplash.com/photo-1587831990711-23ca6441447b?w=400&h=400&fit=crop',
        'televizor': 'https://images.unsplash.com/photo-1593359677879-a4bb92f829d1?w=400&h=400&fit=crop',
        'tv': 'https://images.unsplash.com/photo-1593359677879-a4bb92f829d1?w=400&h=400&fit=crop',
        'naushnik': 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400&h=400&fit=crop',
        'headphone': 'https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400&h=400&fit=crop',
        'airpods': 'https://images.unsplash.com/photo-1606220588913-b3aacb4d2f46?w=400&h=400&fit=crop',
        'soat': 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=400&h=400&fit=crop',
        'watch': 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=400&h=400&fit=crop',
        'smartwatch': 'https://images.unsplash.com/photo-1546868871-7041f2a55e12?w=400&h=400&fit=crop',
        'planshet': 'https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?w=400&h=400&fit=crop',
        'tablet': 'https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?w=400&h=400&fit=crop',
        'ipad': 'https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?w=400&h=400&fit=crop',

        # Kiyim-kechak
        'ko\'ylak': 'https://images.unsplash.com/photo-1596755094514-f87e34085b2c?w=400&h=400&fit=crop',
        'shirt': 'https://images.unsplash.com/photo-1596755094514-f87e34085b2c?w=400&h=400&fit=crop',
        'futbolka': 'https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=400&h=400&fit=crop',
        'tshirt': 'https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?w=400&h=400&fit=crop',
        'shim': 'https://images.unsplash.com/photo-1542272454315-4c01d7abdf4a?w=400&h=400&fit=crop',
        'pants': 'https://images.unsplash.com/photo-1542272454315-4c01d7abdf4a?w=400&h=400&fit=crop',
        'jeans': 'https://images.unsplash.com/photo-1542272454315-4c01d7abdf4a?w=400&h=400&fit=crop',
        'jinsi': 'https://images.unsplash.com/photo-1542272454315-4c01d7abdf4a?w=400&h=400&fit=crop',
        'kurtka': 'https://images.unsplash.com/photo-1551028719-00167b16eac5?w=400&h=400&fit=crop',
        'jacket': 'https://images.unsplash.com/photo-1551028719-00167b16eac5?w=400&h=400&fit=crop',
        'poyabzal': 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400&h=400&fit=crop',
        'shoes': 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400&h=400&fit=crop',
        'krossovka': 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400&h=400&fit=crop',
        'sneakers': 'https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400&h=400&fit=crop',

        # Oziq-ovqat
        'non': 'https://images.unsplash.com/photo-1509440159596-0249088772ff?w=400&h=400&fit=crop',
        'bread': 'https://images.unsplash.com/photo-1509440159596-0249088772ff?w=400&h=400&fit=crop',
        'sut': 'https://images.unsplash.com/photo-1563636619-e9143da7973b?w=400&h=400&fit=crop',
        'milk': 'https://images.unsplash.com/photo-1563636619-e9143da7973b?w=400&h=400&fit=crop',
        'meva': 'https://images.unsplash.com/photo-1619566636858-adf3ef46400b?w=400&h=400&fit=crop',
        'fruit': 'https://images.unsplash.com/photo-1619566636858-adf3ef46400b?w=400&h=400&fit=crop',
        'olma': 'https://images.unsplash.com/photo-1560806887-1e4cd0b6cbd6?w=400&h=400&fit=crop',
        'apple': 'https://images.unsplash.com/photo-1560806887-1e4cd0b6cbd6?w=400&h=400&fit=crop',
        'sabzavot': 'https://images.unsplash.com/photo-1540420773420-3366772f4999?w=400&h=400&fit=crop',
        'vegetable': 'https://images.unsplash.com/photo-1540420773420-3366772f4999?w=400&h=400&fit=crop',
        'go\'sht': 'https://images.unsplash.com/photo-1607623814075-e51df1bdc82f?w=400&h=400&fit=crop',
        'meat': 'https://images.unsplash.com/photo-1607623814075-e51df1bdc82f?w=400&h=400&fit=crop',
        'baliq': 'https://images.unsplash.com/photo-1510130387422-82bed34b37e9?w=400&h=400&fit=crop',
        'fish': 'https://images.unsplash.com/photo-1510130387422-82bed34b37e9?w=400&h=400&fit=crop',
        'shokolad': 'https://images.unsplash.com/photo-1481391319762-47dff72954d9?w=400&h=400&fit=crop',
        'chocolate': 'https://images.unsplash.com/photo-1481391319762-47dff72954d9?w=400&h=400&fit=crop',
        'qahva': 'https://images.unsplash.com/photo-1447933601403-0c6688de566e?w=400&h=400&fit=crop',
        'coffee': 'https://images.unsplash.com/photo-1447933601403-0c6688de566e?w=400&h=400&fit=crop',
        'choy': 'https://images.unsplash.com/photo-1556679343-c7306c1976bc?w=400&h=400&fit=crop',
        'tea': 'https://images.unsplash.com/photo-1556679343-c7306c1976bc?w=400&h=400&fit=crop',

        # Uy-ro'zg'or
        'stol': 'https://images.unsplash.com/photo-1530018607912-eff2daa1bac4?w=400&h=400&fit=crop',
        'table': 'https://images.unsplash.com/photo-1530018607912-eff2daa1bac4?w=400&h=400&fit=crop',
        'stul': 'https://images.unsplash.com/photo-1503602642458-232111445657?w=400&h=400&fit=crop',
        'chair': 'https://images.unsplash.com/photo-1503602642458-232111445657?w=400&h=400&fit=crop',
        'divan': 'https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=400&h=400&fit=crop',
        'sofa': 'https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=400&h=400&fit=crop',
        'krovat': 'https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?w=400&h=400&fit=crop',
        'bed': 'https://images.unsplash.com/photo-1505693416388-ac5ce068fe85?w=400&h=400&fit=crop',
        'shkaf': 'https://images.unsplash.com/photo-1558997519-83ea9252edf8?w=400&h=400&fit=crop',
        'wardrobe': 'https://images.unsplash.com/photo-1558997519-83ea9252edf8?w=400&h=400&fit=crop',
        'lampa': 'https://images.unsplash.com/photo-1507473885765-e6ed057f782c?w=400&h=400&fit=crop',
        'lamp': 'https://images.unsplash.com/photo-1507473885765-e6ed057f782c?w=400&h=400&fit=crop',

        # Sport
        'to\'p': 'https://images.unsplash.com/photo-1579952363873-27f3bade9f55?w=400&h=400&fit=crop',
        'ball': 'https://images.unsplash.com/photo-1579952363873-27f3bade9f55?w=400&h=400&fit=crop',
        'futbol': 'https://images.unsplash.com/photo-1579952363873-27f3bade9f55?w=400&h=400&fit=crop',
        'football': 'https://images.unsplash.com/photo-1579952363873-27f3bade9f55?w=400&h=400&fit=crop',
        'velosiped': 'https://images.unsplash.com/photo-1485965120184-e220f721d03e?w=400&h=400&fit=crop',
        'bicycle': 'https://images.unsplash.com/photo-1485965120184-e220f721d03e?w=400&h=400&fit=crop',
        'gantel': 'https://images.unsplash.com/photo-1534438327276-14e5300c3a48?w=400&h=400&fit=crop',
        'dumbbell': 'https://images.unsplash.com/photo-1534438327276-14e5300c3a48?w=400&h=400&fit=crop',

        # Default
        'default': 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=400&h=400&fit=crop',
    }

    def handle(self, *args, **options):
        self.stdout.write("\n=== MAHSULOTLARGA RASM QO'SHISH ===\n")

        # Media papkasini tekshirish
        products_dir = os.path.join(settings.MEDIA_ROOT, 'products')
        categories_dir = os.path.join(settings.MEDIA_ROOT, 'categories')

        os.makedirs(products_dir, exist_ok=True)
        os.makedirs(categories_dir, exist_ok=True)

        # Kategoriyalarga rasm qo'shish
        self.stdout.write("\n--- KATEGORIYALAR ---")
        categories = Category.objects.all()
        for cat in categories:
            if not cat.image:
                image_url = self.get_category_image_url(cat.name.lower() if cat.name else 'default')
                self.download_and_save_category_image(cat, image_url)

        # Mahsulotlarga rasm qo'shish
        self.stdout.write("\n--- MAHSULOTLAR ---")
        products = Product.objects.all()

        for product in products:
            # Eski rasmlarni o'chirish
            ProductImage.objects.filter(product=product).delete()

            # Yangi rasm qo'shish
            product_name = (product.name or '').lower()
            category_name = (product.category.name if product.category else '').lower()

            image_url = self.get_product_image_url(product_name, category_name)
            self.download_and_save_product_image(product, image_url)

        self.stdout.write(self.style.SUCCESS("\n\nBarcha rasmlar muvaffaqiyatli qo'shildi!"))
        self.stdout.write("Endi serverni qayta ishga tushiring: python manage.py runserver")

    def get_category_image_url(self, category_name):
        """Kategoriya uchun mos rasm URL ni topish"""
        for key, url in self.CATEGORY_IMAGES.items():
            if key in category_name:
                return url
        return self.CATEGORY_IMAGES['default']

    def get_product_image_url(self, product_name, category_name):
        """Mahsulot uchun mos rasm URL ni topish"""
        # Avval mahsulot nomiga qarab
        for key, url in self.PRODUCT_IMAGES.items():
            if key in product_name:
                return url

        # Keyin kategoriya nomiga qarab
        for key, url in self.CATEGORY_IMAGES.items():
            if key in category_name:
                return url

        return self.PRODUCT_IMAGES['default']

    def download_and_save_category_image(self, category, image_url):
        """Kategoriya uchun rasmni yuklab saqlash"""
        try:
            response = requests.get(image_url, timeout=30)
            if response.status_code == 200:
                filename = f"category_{category.id}.jpg"
                filepath = f"categories/{filename}"

                # Faylni saqlash
                full_path = os.path.join(settings.MEDIA_ROOT, filepath)
                with open(full_path, 'wb') as f:
                    f.write(response.content)

                # Database ni yangilash
                category.image = filepath
                category.save()

                self.stdout.write(self.style.SUCCESS(f"  + {category.name}: {filepath}"))
            else:
                self.stdout.write(self.style.ERROR(f"  - {category.name}: Yuklab bo'lmadi (HTTP {response.status_code})"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"  - {category.name}: Xato - {str(e)}"))

    def download_and_save_product_image(self, product, image_url):
        """Mahsulot uchun rasmni yuklab saqlash"""
        try:
            response = requests.get(image_url, timeout=30)
            if response.status_code == 200:
                filename = f"product_{product.id}.jpg"
                filepath = f"products/{filename}"

                # Faylni saqlash
                full_path = os.path.join(settings.MEDIA_ROOT, filepath)
                with open(full_path, 'wb') as f:
                    f.write(response.content)

                # ProductImage yaratish
                ProductImage.objects.create(
                    product=product,
                    image=filepath
                )

                self.stdout.write(self.style.SUCCESS(f"  + {product.name}: {filepath}"))
            else:
                self.stdout.write(self.style.ERROR(f"  - {product.name}: Yuklab bo'lmadi (HTTP {response.status_code})"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"  - {product.name}: Xato - {str(e)}"))
