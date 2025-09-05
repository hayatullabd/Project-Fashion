# Project-Fashion
University Project

To set up the development environment for the Bangladeshi fashion e-commerce Django project (named BengaliBoutique), 

### Development Setup for BengaliBoutique E-commerce Project

#### Prerequisites
- Python 3.8+: Ensure Python is installed (`python --version` or `python3 --version`).
- MySQL: MySQL server installed and running.
- Git: For version control (optional, if cloning from a repository).
- Node.js (optional): For Tailwind CSS development (if customizing beyond CDN).
- Text Editor/IDE: VS Code, PyCharm, or any preferred editor.
- SolaimanLipi Font: Download `SolaimanLipi.ttf` from a reliable source (e.g., open-source font repositories) for Bengali text support.

### Step-by-Step Setup

#### 1. Clone or Create the Project
If the project is in a Git repository:

git clone <repository-url>
cd bengaliboutique

Alternatively, create the project directory manually:
mkdir bengaliboutique
cd bengaliboutique

#### 2. Set Up a Virtual Environment
Create and activate a Python virtual environment to isolate dependencies:
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate


#### 3. Install Dependencies
Create a `requirements.txt` file with the following content (as per the project):

django
mysqlclient
pillow

Install dependencies:
pip install -r requirements.txt

-django: Web framework.
-mysqlclient: MySQL adapter for Django.
-pillow: For image handling (product images).

#### 4. Configure MySQL Database
1. **Install MySQL** (if not installed):
   - Linux (Ubuntu): `sudo apt update && sudo apt install mysql-server`
   - macOS: `brew install mysql`
   - Windows: Download MySQL Community Server from [mysql.com](https://dev.mysql.com/downloads/installer/).
   - Start MySQL: `sudo service mysql start` (Linux) or `mysql.server start` (macOS).

2. **Create Database and User**:
   Log into MySQL:
   mysql -u root -p
   Run the following SQL commands:
   CREATE DATABASE bdfashion_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   CREATE USER 'bduser'@'localhost' IDENTIFIED BY 'bdpass';
   GRANT ALL PRIVILEGES ON bdfashion_db.* TO 'bduser'@'localhost';
   FLUSH PRIVILEGES;
   EXIT;
 

3. **Verify Database Connection**:
   Ensure `bdfashion/settings.py` has the correct database configuration:
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.mysql',
           'NAME': 'bdfashion_db',
           'USER': 'bduser',
           'PASSWORD': 'bdpass',
           'HOST': 'localhost',
           'PORT': '3306',
           'OPTIONS': {
               'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
           },
       }
   }
   ```

#### 5. Set Up Project Structure
Ensure the project structure matches:
```
bengaliboutique/
├── manage.py
├── bdfashion/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   ├── wsgi.py
├── shop/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── migrations/
│   ├── models.py
│   ├── tests.py
│   ├── urls.py
│   ├── views.py
│   ├── forms.py
│   ├── templates/
│   │   └── shop/
│   │       ├── base.html
│   │       ├── home.html
│   │       ├── product_list.html
│   │       ├── product_detail.html
│   │       ├── cart.html
│   │       ├── checkout.html
│   │       ├── register.html
│   │       ├── login.html
│   │       ├── profile.html
│   │       ├── wishlist.html
│   │       ├── order_confirmation.html
├── media/
│   └── products/
├── static/
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   └── script.js
│   ├── fonts/
│   │   └── SolaimanLipi.ttf
├── requirements.txt
```

- Copy the provided code for `settings.py`, `urls.py`, `models.py`, `views.py`, `forms.py`, `admin.py`, `tests.py`, and templates into their respective files.
- Download `SolaimanLipi.ttf` and place it in `static/fonts/`.
- Create `media/products/` for product images.

#### 6. Apply Migrations
Run Django migrations to create database tables:
python manage.py makemigrations shop
python manage.py migrate


#### 7. Create Superuser
Create an admin user for the Django admin panel:
python manage.py createsuperuser
Follow prompts to set username, email, and password.

#### 8. Add Sample Data
Access the admin panel (`http://localhost:8000/admin/`) and log in with the superuser credentials. Add:
- **Categories**: Women, Men, Kids, Accessories (e.g., slugs: `women`, `men`, `kids`, `accessories`).
- **Products**: Example:
  - Name: Silk Saree, Slug: silk-saree, Price: 1500, Original Price: 1800, Discount: 20, Category: Women, Stock: 10, Size: M, Image: Upload to `media/products/`.
  - Name: Cotton Kurta, Slug: cotton-kurta, Price: 800, Category: Men, Stock: 15, Size: L.
- **Product Variants**: Example:
  - Product: Silk Saree, Size: M, Color: Red, Stock: 5, Price: 1500.
  - Product: Silk Saree, Size: L, Color: Blue, Stock: 3, Price: 1600.
- **Reviews**: Add a few reviews for products via the admin panel.

Alternatively, use a Django management command to seed data:
# shop/management/commands/seed_data.py
from django.core.management.base import BaseCommand
from shop.models import Category, Product, ProductVariant

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        categories = [
            {'name': 'Women', 'slug': 'women'},
            {'name': 'Men', 'slug': 'men'},
            {'name': 'Kids', 'slug': 'kids'},
            {'name': 'Accessories', 'slug': 'accessories'},
        ]
        for cat in categories:
            Category.objects.get_or_create(**cat)
        
        products = [
            {'name': 'Silk Saree', 'slug': 'silk-saree', 'description': 'Elegant silk saree', 'price': 1500, 'original_price': 1800, 'discount': 20, 'category': Category.objects.get(slug='women'), 'stock': 10, 'size': 'M'},
            {'name': 'Cotton Kurta', 'slug': 'cotton-kurta', 'description': 'Comfortable kurta', 'price': 800, 'category': Category.objects.get(slug='men'), 'stock': 15, 'size': 'L'},
        ]
        for prod in products:
            Product.objects.get_or_create(**prod)
        
        variants = [
            {'product': Product.objects.get(slug='silk-saree'), 'size': 'M', 'color': 'Red', 'stock': 5, 'price': 1500},
            {'product': Product.objects.get(slug='silk-saree'), 'size': 'L', 'color': 'Blue', 'stock': 3, 'price': 1600},
        ]
        for var in variants:
            ProductVariant.objects.get_or_create(**var)
        
        self.stdout.write(self.style.SUCCESS('Sample data added'))

Run: python manage.py seed_data

#### 9. Configure Static and Media Files
Ensure `settings.py` includes:

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```
Create directories:

mkdir -p static/css static/js static/fonts media/products


#### 10. Run Development Server
Start the Django development server:

python manage.py runserver

Access the site at `http://localhost:8000`.

#### 11. Test the Application
- **Admin Panel**: `http://localhost:8000/admin/`
- **Homepage**: `http://localhost:8000/`
- **Product List**: `http://localhost:8000/products/`
- **Cart, Checkout, Profile, Wishlist**: Test all features.
- **Run Tests**:
  python manage.py test shop


#### 12. Optional: Tailwind CSS Development
The project uses Tailwind via CDN. For local development (to customize Tailwind):
1. Install Node.js: `https://nodejs.org/`
2. Initialize a Node project:
   npm init -y
   npm install tailwindcss

3. Create `tailwind.config.js`:
   ```javascript
   module.exports = {
       content: ['./templates/**/*.html'],
       theme: { extend: {} },
       plugins: [],
   }
   ```
4. Create `static/css/input.css`:
   ```css
   @tailwind base;
   @tailwind components;
   @tailwind utilities;
   ```
5. Build Tailwind:
   ```bash
   npx tailwindcss -i static/css/input.css -o static/css/style.css --watch
   ```
6. Update `base.html` to use local Tailwind:
   ```html
   <link rel="stylesheet" href="{% static 'css/style.css' %}">
   ```

#### 13. Debugging Tips
- **Database Issues**: Check MySQL connection (`mysql -u bduser -p bdfashion_db`).
- **Static Files**: Run `python manage.py collectstatic` if static files don’t load.
- **Template Errors**: Verify template paths and `{% load static %}`.
- **CSRF Errors**: Ensure `{% csrf_token %}` in forms and correct headers in AJAX requests.

#### 14. Development Workflow
- **Version Control**: Initialize Git:
  ```bash
  git init
  echo "venv/\n*.pyc\n__pycache__/\nmedia/\nstaticfiles/" > .gitignore
  git add .
  git commit -m "Initial commit"
  ```
- **Code Formatting**: Use `black` or `flake8`:
  ```bash
  pip install black flake8
  black .
  flake8 .
  ```
- **Environment Variables**: Use `python-decouple` for sensitive settings:
  ```bash
  pip install python-decouple
  ```
  Create `.env`:
  ```
  SECRET_KEY=your-secret-key
  DATABASE_NAME=bdfashion_db
  DATABASE_USER=bduser
  DATABASE_PASSWORD=bdpass
  ```
  Update `settings.py`:
  ```python
  from decouple import config
  SECRET_KEY = config('SECRET_KEY')
  DATABASES['default']['NAME'] = config('DATABASE_NAME')
  DATABASES['default']['USER'] = config('DATABASE_USER')
  DATABASES['default']['PASSWORD'] = config('DATABASE_PASSWORD')
  ```

---

### Notes
- **Font**: Ensure `SolaimanLipi.ttf` is in `static/fonts/` for Bengali text.
- **Images**: Upload product images to `media/products/` via admin or manually.
- **Testing**: Test all features (cart, wishlist, checkout, filters, search) on multiple browsers/devices.
- **Next Steps**: For production, configure Gunicorn, Nginx, and SSL as outlined previously. Add a real payment gateway (e.g., SSLCommerz) for Bangladesh.