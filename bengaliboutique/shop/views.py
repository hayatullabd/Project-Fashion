from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from django.db.models import Q, Avg
from django.core.mail import send_mail
from .models import Category, Product, Order, OrderItem, Review, Wishlist, ProductVariant
from .forms import UserRegistrationForm, ReviewForm
import json

def home(request):
    featured_products = Product.objects.all()[:6]
    categories = Category.objects.all()
    reviews = Review.objects.all()[:3]
    return render(request, 'shop/home.html', {'featured_products': featured_products, 'categories': categories, 'reviews': reviews})

def product_list(request):
    category_slug = request.GET.get('category')
    sort = request.GET.get('sort', 'name')
    query = request.GET.get('q')
    size = request.GET.get('size')
    price_min = request.GET.get('price_min')
    price_max = request.GET.get('price_max')
    page = int(request.GET.get('page', 1))
    per_page = 12

    products = Product.objects.all()
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
    if query:
        products = products.filter(Q(name__icontains=query) | Q(description__icontains=query))
    if size:
        products = products.filter(size__icontains=size)
    if price_min:
        products = products.filter(price__gte=price_min)
    if price_max:
        products = products.filter(price__lte=price_max)
    if sort == 'price_asc':
        products = products.order_by('price')
    elif sort == 'price_desc':
        products = products.order_by('-price')
    elif sort == 'newest':
        products = products.order_by('-id')
    elif sort == 'rating':
        products = products.annotate(avg_rating=Avg('reviews__rating')).order_by('-avg_rating')

    total = products.count()
    products = products[(page-1)*per_page:page*per_page]
    categories = Category.objects.all()
    return render(request, 'shop/product_list.html', {'products': products, 'total': total, 'page': page, 'per_page': per_page, 'categories': categories})

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    reviews = product.reviews.all()
    if request.method == 'POST' and request.user.is_authenticated:
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            messages.success(request, 'Review added!')
            return redirect('product_detail', slug=slug)
    else:
        form = ReviewForm()
    return render(request, 'shop/product_detail.html', {'product': product, 'reviews': reviews, 'form': form})

def get_cart(request):
    return request.session.get('cart', {})

def cart_add(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    variant_id = request.POST.get('variant_id') or request.GET.get('variant_id')
    if variant_id:
        variant = get_object_or_404(ProductVariant, id=variant_id, product=product)
        if variant.stock < 1:
            return JsonResponse({'success': False, 'error': 'Out of stock'}, status=400)
        cart = get_cart(request)
        cart_key = f"{product_id}:{variant_id}"
        current_qty = cart.get(cart_key, 0)
        if current_qty + 1 > variant.stock:
            return JsonResponse({'success': False, 'error': 'Exceeds stock'}, status=400)
        cart[cart_key] = current_qty + 1
    else:
        if product.stock < 1:
            return JsonResponse({'success': False, 'error': 'Out of stock'}, status=400)
        cart = get_cart(request)
        current_qty = cart.get(str(product_id), 0)
        if current_qty + 1 > product.stock:
            return JsonResponse({'success': False, 'error': 'Exceeds stock'}, status=400)
        cart[str(product_id)] = current_qty + 1
    request.session['cart'] = cart
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'cart_total': sum(cart.values())})
    return redirect('cart_detail')

def cart_remove(request, product_id):
    cart = get_cart(request)
    variant_id = request.POST.get('variant_id') or request.GET.get('variant_id')
    cart_key = f"{product_id}:{variant_id}" if variant_id else str(product_id)
    if cart_key in cart:
        del cart[cart_key]
    request.session['cart'] = cart
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    return redirect('cart_detail')

def cart_detail(request):
    cart = get_cart(request)
    cart_items = []
    total = 0
    for cart_key, quantity in cart.items():
        if ':' in cart_key:
            product_id, variant_id = cart_key.split(':')
            product = get_object_or_404(Product, id=product_id)
            variant = get_object_or_404(ProductVariant, id=variant_id)
            price = variant.price or product.price
            cart_items.append({
                'product': product,
                'variant': variant,
                'quantity': quantity,
                'total': price * quantity
            })
            total += price * quantity
        else:
            product = get_object_or_404(Product, id=cart_key)
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'total': product.price * quantity
            })
            total += product.price * quantity
    return render(request, 'shop/cart.html', {'cart_items': cart_items, 'total': total})

@login_required
def checkout(request):
    if request.method == 'POST':
        cart = get_cart(request)
        if not cart:
            messages.error(request, 'Cart is empty')
            return redirect('cart_detail')
        order = Order.objects.create(
            user=request.user,
            billing_address=request.POST.get('billing_address', request.POST.get('shipping_address')),
            shipping_address=request.POST.get('shipping_address'),
            total_price=0,
            payment_method=request.POST.get('payment')
        )
        total = 100  # Shipping fee
        for cart_key, qty in cart.items():
            if ':' in cart_key:
                product_id, variant_id = cart_key.split(':')
                product = get_object_or_404(Product, id=product_id)
                variant = get_object_or_404(ProductVariant, id=variant_id)
                if qty > variant.stock:
                    order.delete()
                    messages.error(request, 'Stock changed, please update cart')
                    return redirect('cart_detail')
                price = (variant.price or product.price) * qty
                OrderItem.objects.create(order=order, product=product, variant=variant, quantity=qty, price=price)
                variant.stock -= qty
                variant.save()
                total += price
            else:
                product = get_object_or_404(Product, id=cart_key)
                if qty > product.stock:
                    order.delete()
                    messages.error(request, 'Stock changed, please update cart')
                    return redirect('cart_detail')
                price = product.price * qty
                OrderItem.objects.create(order=order, product=product, quantity=qty, price=price)
                product.stock -= qty
                product.save()
                total += price
        order.total_price = total
        order.save()
        send_mail(
            'Order Confirmation',
            f'Your order #{order.id} has been placed. Total: ৳{total}',
            'admin@bengaliboutique.com',
            [request.user.email],
            fail_silently=False,
        )
        send_mail(
            'New Order Placed',
            f'Order #{order.id} by {request.user.username} for ৳{total}',
            'admin@bengaliboutique.com',
            ['admin@bengaliboutique.com'],
            fail_silently=False,
        )
        del request.session['cart']
        return redirect('order_confirmation', order_id=order.id)
    cart = get_cart(request)
    cart_items = []
    total = 0
    for cart_key, quantity in cart.items():
        if ':' in cart_key:
            product_id, variant_id = cart_key.split(':')
            product = get_object_or_404(Product, id=product_id)
            variant = get_object_or_404(ProductVariant, id=variant_id)
            price = variant.price or product.price
            cart_items.append({
                'product': product,
                'variant': variant,
                'quantity': quantity,
                'total': price * quantity
            })
            total += price * quantity
        else:
            product = get_object_or_404(Product, id=cart_key)
            cart_items.append({
                'product': product,
                'quantity': quantity,
                'total': product.price * quantity
            })
            total += product.price * quantity
    return render(request, 'shop/checkout.html', {'cart_items': cart_items, 'total': total})

@login_required
def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'shop/order_confirmation.html', {'order': order})

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('home')
    else:
        form = UserRegistrationForm()
    return render(request, 'shop/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid credentials')
    return render(request, 'shop/login.html')

def user_logout(request):
    logout(request)
    return redirect('home')

@login_required
def profile(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'shop/profile.html', {'orders': orders})

@login_required
def wishlist_add(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    Wishlist.objects.get_or_create(user=request.user, product=product)
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    return redirect('wishlist')

@login_required
def wishlist_remove(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    Wishlist.objects.filter(user=request.user, product=product).delete()
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    return redirect('wishlist')

@login_required
def wishlist_view(request):
    wishlist_items = Wishlist.objects.filter(user=request.user)
    return render(request, 'shop/wishlist.html', {'wishlist_items': wishlist_items})

def cart_update_ajax(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        product_id = data['product_id']
        variant_id = data.get('variant_id')
        quantity = data['quantity']
        cart_key = f"{product_id}:{variant_id}" if variant_id else str(product_id)
        if variant_id:
            variant = get_object_or_404(ProductVariant, id=variant_id)
            if quantity > variant.stock:
                return JsonResponse({'success': False, 'error': 'Exceeds stock'}, status=400)
        else:
            product = get_object_or_404(Product, id=product_id)
            if quantity > product.stock:
                return JsonResponse({'success': False, 'error': 'Exceeds stock'}, status=400)
        cart = get_cart(request)
        if quantity > 0:
            cart[cart_key] = quantity
        else:
            del cart[cart_key]
        request.session['cart'] = cart
        return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=400)

def product_filter_ajax(request):
    category_slug = request.GET.get('category')
    sort = request.GET.get('sort', 'name')
    query = request.GET.get('q')
    size = request.GET.get('size')
    price_min = request.GET.get('price_min')
    price_max = request.GET.get('price_max')

    products = Product.objects.all()
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
    if query:
        products = products.filter(Q(name__icontains=query) | Q(description__icontains=query))
    if size:
        products = products.filter(size__icontains=size)
    if price_min:
        products = products.filter(price__gte=price_min)
    if price_max:
        products = products.filter(price__lte=price_max)
    if sort == 'price_asc':
        products = products.order_by('price')
    elif sort == 'price_desc':
        products = products.order_by('-price')
    elif sort == 'newest':
        products = products.order_by('-id')
    elif sort == 'rating':
        products = products.annotate(avg_rating=Avg('reviews__rating')).order_by('-avg_rating')

    data = [{
        'id': p.id,
        'name': p.name,
        'price': str(p.price),
        'original_price': str(p.original_price) if p.original_price else None,
        'discount': p.discount,
        'image': p.image.url,
        'slug': p.slug,
        'description': p.description
    } for p in products]
    return JsonResponse({'products': data})