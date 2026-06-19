import uuid
import requests
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from cart.cart import Cart
from store.models import Product, Order
from store.forms import CartAddProductForm

# --- CART FUNCTIONALITY ---

def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))
    cart.add(product=product, quantity=quantity, override_quantity=False)
    return redirect('cart:cart_detail')

def cart_detail(request):
    cart = Cart(request)
    cart_items = list(cart)
    total_price = cart.get_total_price()

    for item in cart_items:
        item['update_quantity_form'] = CartAddProductForm(
            initial={
                'quantity': item['quantity'],
                'override': True
            }
        )

    context = {
        'cart_items': cart_items,
        'total_price': total_price,
        'CartAddProductForm': CartAddProductForm,
    }
    return render(request, 'cart/cart.html', context)

def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect('cart:cart_detail')

def cart_clear(request):
    cart = Cart(request)
    cart.clear()
    return redirect('cart:cart_detail')

def cart_update(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    form = CartAddProductForm(request.POST)

    if form.is_valid():
        cd = form.cleaned_data
        cart.add(
            product=product,
            quantity=cd['quantity'],
            override_quantity=cd['override']
        )
    return redirect('cart:cart_detail')


# --- CHECKOUT & PAYSTACK LOGIC ---

def checkout(request):
    cart = Cart(request)
    
    if request.method == 'POST':
        # 1. Generate unique reference
        transaction_ref = str(uuid.uuid4())
        
        # 2. Create the Order in your DB (linked to user if logged in)
        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            full_name=request.POST.get('full_name'),
            email=request.POST.get('email'),
            total_price=cart.get_total_price(),
            transaction_ref=transaction_ref
        )

        # 3. Prepare Paystack data
        url = "https://api.paystack.co/transaction/initialize"
        headers = {
            "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
            "Content-Type": "application/json",
        }
        data = {
            "email": order.email,
            "amount": int(order.total_price * 100),  # Paystack counts in Kobo/Cents
            "reference": transaction_ref,
            "callback_url": "http://127.0.0.1:8000/cart/verify-payment/"
        }

        # 4. Request Payment URL from Paystack
        try:
            response = requests.post(url, headers=headers, json=data)
            res_data = response.json()

            if res_data['status']:
                # Redirect user to Paystack's secure payment page
                return redirect(res_data['data']['authorization_url'])
            else:
                return render(request, 'cart/failure.html', {'error': 'Paystack initialization failed.'})
        except requests.exceptions.RequestException:
            return render(request, 'cart/failure.html', {'error': 'Connection to Paystack failed.'})

    # If GET request, just show the checkout page
    return render(request, 'cart/checkout.html', {'cart': cart})


def verify_payment(request):
    reference = request.GET.get('reference')
    url = f"https://api.paystack.co/transaction/verify/{reference}"
    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
    }

    try:
        response = requests.get(url, headers=headers)
        res_data = response.json()

        if res_data['status'] and res_data['data']['status'] == 'success':
            # Mark order as paid
            order = Order.objects.get(transaction_ref=reference)
            order.paid = True
            order.save()
            
            # Clear the session cart
            cart = Cart(request)
            cart.clear()
            
            return render(request, 'cart/success.html', {'order': order})
    except (requests.exceptions.RequestException, Order.DoesNotExist):
        pass

    return render(request, 'cart/failure.html')

