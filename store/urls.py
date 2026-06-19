from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('register/', views.signup_view, name='register'),
    path('seller/dashboard/', views.seller_dashboard, name='seller_dashboard'),
    path('my-orders/', views.order_history, name='order_history'),
    path('add-product/', views.add_product, name='add_product'),
    path('product/edit/<int:id>/', views.edit_product, name='edit_product'),
    path('product/delete/<int:id>/', views.delete_product, name='delete_product'),
    path('<slug:category_slug>/', views.product_list, name='product_list_by_category'),
    path('<int:id>/<slug:slug>/', views.product_detail, name='product_detail'),
    path('seller/verify/', views.fica_verification, name='fica_verification'),
]

