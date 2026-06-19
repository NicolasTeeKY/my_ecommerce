# my_ecommerce/urls.py (Main Project URLs)
from django.contrib import admin
from django.urls import path, include
# 👇 REQUIRED IMPORTS for serving media in development
from django.conf import settings
from django.conf.urls.static import static 
from store.views import signup_view


urlpatterns = [
    path('admin/', admin.site.urls),
    path('cart/', include('cart.urls', namespace='cart')),
    path('accounts/', include('django.contrib.auth.urls')), # This adds login/logout
    # Point the root URL (or a sub-path) to your store application
    path('accounts/signup/', signup_view, name='signup'),    # Your custom signup
    path('', include('store.urls', namespace='store')),
    path('orders/', include('orders.urls', namespace='orders')),
]

# 👇 IMPORTANT: Configure URL patterns to serve media only if DEBUG is True
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
