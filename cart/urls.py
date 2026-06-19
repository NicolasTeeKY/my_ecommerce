from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    # Shows the cart content
    path('', views.cart_detail, name='cart_detail'),
    
    # Adds a product to the cart (called from the product detail page)
    path('add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('remove/<int:product_id>/', views.cart_remove, name='cart_remove'),
    path('update/<int:product_id>/', views.cart_update, name='cart_update'),
    path('checkout/', views.checkout, name='checkout'),
    path('verify-payment/', views.verify_payment, name='verify_payment'),
    # Add checkout URL when ready                     # path('checkout/', views.checkout, name='checkout'),
]
