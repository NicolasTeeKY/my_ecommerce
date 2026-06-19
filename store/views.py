from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.text import slugify
from django.utils import timezone
from .models import Category, Product, Order
from .forms import SignUpForm, ProductForm, FicaUploadForm

# --- HELPERS ---

def is_verified_seller(user):
    """Checks if a user is a seller AND has passed FICA verification."""
    return user.is_authenticated and user.is_seller and user.is_fica_verified

# --- PUBLIC VIEWS ---

def product_list(request, category_slug=None):
    categories = Category.objects.all()
    products = Product.objects.filter(available=True, is_approved=True)
    category = None
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
    return render(request, 'store/product/list.html', {
        'category': category,
        'categories': categories,
        'products': products
    })

def product_detail(request, id, slug):
    product = get_object_or_404(Product, id=id, slug=slug, available=True)
    return render(request, 'store/product/detail.html', {'product': product})

def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful!")
            return redirect('store:product_list')
    else:
        form = SignUpForm()
    return render(request, 'registration/register.html', {'form': form})

# --- BUYER VIEWS ---

@login_required
def order_history(request):
    # Fixed field name to 'created_at' to match your updated Order model
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'store/order_history.html', {'orders': orders})

# --- FICA VERIFICATION VIEW ---

@login_required
def fica_verification(request):
    if request.method == 'POST':
        form = FicaUploadForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            user = form.save(commit=False)
            user.fica_submitted_at = timezone.now()
            user.save()
            messages.info(request, "FICA documents submitted! Approval usually takes 24-48 hours.")
            return redirect('store:seller_dashboard')
    else:
        form = FicaUploadForm(instance=request.user)
    return render(request, 'store/seller/fica_upload.html', {'form': form})

# --- SELLER DASHBOARD (Accessible to all sellers to see status) ---

@login_required
@user_passes_test(lambda u: u.is_seller)
def seller_dashboard(request):
    my_products = Product.objects.filter(seller=request.user).order_by('-created')
    return render(request, 'store/seller/dashboard.html', {
        'my_products': my_products
    })

# --- PROTECTED SELLER ACTIONS (Require FICA Verification) ---

@login_required
@user_passes_test(is_verified_seller, login_url='store:fica_verification')
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.seller = request.user
            product.is_approved = False  # Still requires admin product approval
            product.slug = slugify(product.name)
            product.save()
            messages.success(request, "Product submitted! It will appear after admin review.")
            return redirect('store:seller_dashboard')
    else:
        form = ProductForm()
    return render(request, 'store/product/add_product.html', {'form': form})

@login_required
@user_passes_test(is_verified_seller, login_url='store:fica_verification')
def edit_product(request, id):
    product = get_object_or_404(Product, id=id, seller=request.user)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            product = form.save(commit=False)
            product.is_approved = False 
            product.save()
            messages.success(request, "Product updated and sent for re-approval.")
            return redirect('store:seller_dashboard')
    else:
        form = ProductForm(instance=product)
    return render(request, 'store/product/add_product.html', {
        'form': form, 
        'edit_mode': True, 
        'product': product
    })

@login_required
@user_passes_test(is_verified_seller, login_url='store:fica_verification')
def delete_product(request, id):
    product = get_object_or_404(Product, id=id, seller=request.user)
    if request.method == 'POST':
        product.delete()
        messages.success(request, "Product deleted successfully.")
    return redirect('store:seller_dashboard')


import uuid
from django.shortcuts import render, redirect
from .forms import CheckoutForm
from .models import Order
from cart.cart import Cart # Assuming your cart logic is in a cart app

def checkout(request):
    cart = Cart(request)
    if len(cart) == 0:
        return redirect('store:product_list')

    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            if request.user.is_authenticated:
                order.user = request.user

            # Generate unique ref and calculate total
            order.transaction_ref = str(uuid.uuid4()).split('-')[0].upper()
            order.total_price = cart.get_total_price()
            order.save()

            # Store the order ID in the session for the payment page
            request.session['order_id'] = order.id
            return redirect('store:payment_process') # We will create this next
    else:
        form = CheckoutForm()

    return render(request, 'store/order/checkout.html', {'cart': cart, 'form': form})

