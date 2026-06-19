from django.contrib import admin

# Register your models here.

from django.contrib import admin
from .models import Cart, CartItem

# Register the models
admin.site.register(Cart)
admin.site.register(CartItem)

