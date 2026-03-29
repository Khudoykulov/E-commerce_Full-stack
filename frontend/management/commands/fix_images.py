"""
Mahsulot va kategoriya rasmlarini tekshirish va tuzatish
"""
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from apps.product.models import Product, ProductImage, Category


class Command(BaseCommand):
    help = 'Mahsulot va kategoriya rasmlarini tekshirish'

    def handle(self, *args, **options):
        self.stdout.write("\n=== RASMLAR HOLATI ===\n")

        # Media papkasini tekshirish
        media_root = settings.MEDIA_ROOT
        self.stdout.write(f"MEDIA_ROOT: {media_root}")
        self.stdout.write(f"MEDIA_URL: {settings.MEDIA_URL}")

        # Products papkasidagi rasmlar
        products_dir = os.path.join(media_root, 'products')
        if os.path.exists(products_dir):
            product_files = os.listdir(products_dir)
            self.stdout.write(f"\nMedia/products papkasida {len(product_files)} ta fayl mavjud")
        else:
            self.stdout.write(self.style.ERROR(f"\nMedia/products papkasi mavjud emas!"))
            product_files = []

        # Categories papkasidagi rasmlar
        categories_dir = os.path.join(media_root, 'categories')
        if os.path.exists(categories_dir):
            category_files = os.listdir(categories_dir)
            self.stdout.write(f"Media/categories papkasida {len(category_files)} ta fayl mavjud")
        else:
            self.stdout.write(self.style.ERROR(f"Media/categories papkasi mavjud emas!"))
            category_files = []

        # Database dagi mahsulotlar
        products = Product.objects.all()
        self.stdout.write(f"\nDatabase da {products.count()} ta mahsulot mavjud")

        # Rasmsiz mahsulotlar
        products_without_images = []
        for product in products:
            if not product.images.exists():
                products_without_images.append(product)

        self.stdout.write(f"Rasmsiz mahsulotlar: {len(products_without_images)} ta")

        # Rasmli mahsulotlar
        product_images = ProductImage.objects.all()
        self.stdout.write(f"ProductImage jadvalida {product_images.count()} ta yozuv mavjud")

        # Kategoriyalar
        categories = Category.objects.all()
        categories_without_images = categories.filter(image='').count() + categories.filter(image__isnull=True).count()
        self.stdout.write(f"\nDatabase da {categories.count()} ta kategoriya mavjud")
        self.stdout.write(f"Rasmsiz kategoriyalar: {categories_without_images} ta")

        # Rasmlarni ko'rsatish
        self.stdout.write("\n=== MAHSULOT RASMLARI ===")
        for pi in product_images[:10]:
            self.stdout.write(f"  ID: {pi.id}, Product: {pi.product_id}, Path: {pi.image}")

        self.stdout.write("\n=== KATEGORIYA RASMLARI ===")
        for cat in categories[:10]:
            self.stdout.write(f"  ID: {cat.id}, Name: {cat.name}, Image: {cat.image}")

        # Rasmsiz mahsulotlarga rasm qo'shish
        if products_without_images and product_files:
            self.stdout.write(self.style.WARNING(f"\n=== RASMLARNI QO'SHISH ==="))

            # Har bir rasmsiz mahsulotga bitta rasm qo'shish
            for i, product in enumerate(products_without_images):
                if i < len(product_files):
                    image_path = f"products/{product_files[i]}"
                    ProductImage.objects.create(
                        product=product,
                        image=image_path
                    )
                    self.stdout.write(f"  + {product.name}: {image_path}")

            self.stdout.write(self.style.SUCCESS(f"\n{min(len(products_without_images), len(product_files))} ta mahsulotga rasm qo'shildi!"))

        # Rasmsiz kategoriyalarga rasm qo'shish
        categories_without = Category.objects.filter(image='') | Category.objects.filter(image__isnull=True)
        if categories_without.exists() and category_files:
            self.stdout.write(self.style.WARNING(f"\n=== KATEGORIYA RASMLARINI QO'SHISH ==="))

            for i, cat in enumerate(categories_without):
                if i < len(category_files):
                    image_path = f"categories/{category_files[i]}"
                    cat.image = image_path
                    cat.save()
                    self.stdout.write(f"  + {cat.name}: {image_path}")

            self.stdout.write(self.style.SUCCESS(f"\n{min(categories_without.count(), len(category_files))} ta kategoriyaga rasm qo'shildi!"))

        self.stdout.write(self.style.SUCCESS("\nTayyor!"))
