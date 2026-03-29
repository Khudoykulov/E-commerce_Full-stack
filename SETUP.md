# Wholesale App - O'rnatish yo'riqnomasi

## Talablar
- Python 3.10+
- PostgreSQL 13+

## O'rnatish

### 1. Virtual muhit yaratish
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 2. Kutubxonalarni o'rnatish
```bash
pip install -r requirements.txt
```

### 3. PostgreSQL database yaratish
```sql
CREATE DATABASE wholesale_db;
```

### 4. .env faylini sozlash
`.env` faylini yarating va quyidagilarni yozing:
```
SECRET_KEY=your-secret-key-here
DEBUG=1
DB_NAME=wholesale_db
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=your-password
```

### 5. Migratsiyalarni bajarish
```bash
python manage.py migrate
```

### 6. Test ma'lumotlarini yuklash
```bash
python manage.py loaddata database_fixture.json
```

### 7. Serverni ishga tushirish
```bash
python manage.py runserver
```

## Foydalanish

- **Sayt**: http://127.0.0.1:8000/
- **Admin panel**: http://127.0.0.1:8000/admin/
- **API Documentation**: http://127.0.0.1:8000/swagger/

## Test foydalanuvchi
Agar test foydalanuvchi yaratilgan bo'lsa, tizimga kirish uchun ishlatishingiz mumkin.

## Muammolar

Agar rasmlar ko'rinmasa:
```bash
python manage.py setup_product_images
```

Bu buyruq mahsulotlar uchun rasmlarni yuklab qo'shadi.
