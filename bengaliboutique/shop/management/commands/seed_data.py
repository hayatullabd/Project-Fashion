from django.core.management.base import BaseCommand
from shop.models import Category, Product, ProductVariant

class Command(BaseCommand):
    help = 'Seeds the database with sample data'

    def handle(self, *args, **kwargs):
        categories = [
            {'name': 'Women', 'slug': 'women', 'description': 'Women’s clothing'},
            {'name': 'Men', 'slug': 'men', 'description': 'Men’s clothing'},
            {'name': 'Kids', 'slug': 'kids', 'description': 'Kids’ clothing'},
            {'name': 'Accessories', 'slug': 'accessories', 'description': 'Fashion accessories'},
        ]
        for cat in categories:
            Category.objects.get_or_create(**cat)
        
        products = [
            {'name': 'Silk Saree', 'slug': 'silk-saree', 'description': 'Elegant silk saree for special occasions', 'price': 1500, 'original_price': 1800, 'discount': 20, 'category': Category.objects.get(slug='women'), 'stock': 10, 'size': 'M'},
            {'name': 'Cotton Kurta', 'slug': 'cotton-kurta', 'description': 'Comfortable kurta for daily wear', 'price': 800, 'category': Category.objects.get(slug='men'), 'stock': 15, 'size': 'L'},
            {'name': 'Kids Lehenga', 'slug': 'kids-lehenga', 'description': 'Festive lehenga for kids', 'price': 1200, 'category': Category.objects.get(slug='kids'), 'stock': 8, 'size': 'S'},
        ]
        for prod in products:
            Product.objects.get_or_create(**prod)
        
        variants = [
            {'product': Product.objects.get(slug='silk-saree'), 'size': 'M', 'color': 'Red', 'stock': 5, 'price': 1500},
            {'product': Product.objects.get(slug='silk-saree'), 'size': 'L', 'color': 'Blue', 'stock': 3, 'price': 1600},
        ]
        for var in variants:
            ProductVariant.objects.get_or_create(**var)
        
        self.stdout.write(self.style.SUCCESS('Sample data added successfully'))