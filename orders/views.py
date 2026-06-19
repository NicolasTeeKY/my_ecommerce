import uuid
import requests
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from cart.cart import Cart
from store.models import Order  # Using the Order model you already have
from django.contrib import messages

def order_create(request):
    cart = Cart(request)
    
    if request.method == 'POST':
        # 1. Generate unique reference
        transaction_ref = str(uuid.uuid4())

        # 2. Create the Order in your DB (using your existing model fields)
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
            "amount": int(order.total_price * 100),  # Amount in kobo
            "reference": transaction_ref,
            "callback_url": request.build_absolute_uri('/orders/verify-payment/')
        }

        # 4. Request Payment URL from Paystack
        try:
            response = requests.post(url, headers=headers, json=data)
            res_data = response.json()

            if res_data.get('status'):
                # Redirect user to Paystack
                return redirect(res_data['data']['authorization_url'])
            else:
                return render(request, 'cart/failure.html', {'error': 'Paystack initialization failed.'})
        except requests.exceptions.RequestException:
            return render(request, 'cart/failure.html', {'error': 'Connection to Paystack failed.'})

    # Use your existing cart/checkout.html template
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

            # Use your existing success template
            return render(request, 'cart/success.html', {'order': order})
    except (requests.exceptions.RequestException, Order.DoesNotExist):
        pass

    # Use your existing failure template
    return render(request, 'cart/failure.html')

