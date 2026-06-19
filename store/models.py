from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser

# 1. THE USER MODEL
class User(AbstractUser):
    is_seller = models.BooleanField(default=False)
    is_buyer = models.BooleanField(default=True)                                                                                                                                 
    
    # FICA FIELDS
    is_fica_verified = models.BooleanField(default=False)
    id_document = models.FileField(upload_to='fica/ids/', blank=True, null=True)
    proof_of_address = models.FileField(upload_to='fica/address/', blank=True, null=True)
    fica_submitted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.username

# 2. THE CATEGORY MODEL
class Category(models.Model):
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True)

    class Meta:
        ordering = ('name',)
        verbose_name = 'category'
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name

# 3. THE PRODUCT MODEL
class Product(models.Model):
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='products_sold')
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True)
    image = models.ImageField(upload_to='products/%Y/%m/%d', blank=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    available = models.BooleanField(default=True)
    is_approved = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-created',)
        indexes = [models.Index(fields=['id', 'slug']),]

    def __str__(self):
        return self.name

# 4. THE ORDER MODEL
class Order(models.Model):
    PROVINCE_CHOICES = [
        ('GP', 'Gauteng'), ('WC', 'Western Cape'), ('KZN', 'KwaZulu-Natal'),
        ('FS', 'Free State'), ('EC', 'Eastern Cape'), ('NW', 'North West'),
        ('MP', 'Mpumalanga'), ('LP', 'Limpopo'), ('NC', 'Northern Cape')
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, related_name='orders')

    # --- Shipping Fields ---
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    address = models.CharField(max_length=250)
    city = models.CharField(max_length=100)
    province = models.CharField(max_length=50, choices=PROVINCE_CHOICES)
    postal_code = models.CharField(max_length=10)

    # --- Payment & Status ---
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_ref = models.CharField(max_length=100, unique=True)
    paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return f"Order {self.transaction_ref} - {self.full_name}"

# 5. THE ORDER ITEM MODEL (Critical for tracking sales)

