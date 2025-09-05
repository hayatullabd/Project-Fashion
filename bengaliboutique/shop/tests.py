from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Category, Product, ProductVariant, Order, OrderItem, Wishlist

class ModelTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.category = Category.objects.create(name='Women', slug='women')
        self.product = Product.objects.create(name='Silk Saree', slug='silk-saree', price=1500, original_price=1800, discount=20, category=self.category, stock=10, description='Elegant saree')

    def test_product_creation(self):
        self.assertEqual(self.product.name, 'Silk Saree')
        self.assertEqual(self.product.stock, 10)

    def test_order_creation(self):
        order = Order.objects.create(user=self.user, total_price=1500)
        OrderItem.objects.create(order=order, product=self.product, quantity=1, price=1500)
        self.assertEqual(order.items.count(), 1)

class ViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.category = Category.objects.create(name='Women', slug='women')
        self.product = Product.objects.create(name='Silk Saree', slug='silk-saree', price=1500, category=self.category, stock=10)

    def test_home_page(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

    def test_add_to_cart(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.post(reverse('cart_add', args=[self.product.id]))
        self.assertEqual(response.status_code, 302)
        self.assertIn(str(self.product.id), self.client.session['cart'])