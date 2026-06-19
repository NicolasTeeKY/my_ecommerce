from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from .models import User, Category, Product, Order

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'is_seller', 'fica_status', 'view_id', 'view_proof']
    list_filter = ['is_fica_verified', 'is_seller']
    search_fields = ['username', 'email']
    actions = ['approve_fica', 'reject_fica']

    # We use mark_safe for static HTML strings to avoid the format_html error
    def fica_status(self, obj):
        if obj.is_fica_verified:
            return mark_safe('<span style="color: #2ecc71; font-weight: bold;">Verified ✅</span>')
        if obj.fica_submitted_at:
            return mark_safe('<span style="color: #f39c12; font-weight: bold;">Review Pending ⏳</span>')
        return "Not Submitted"
    fica_status.short_description = 'FICA Status'

    # We use format_html when we actually have a variable (the URL) to inject
    def view_id(self, obj):
        if obj.id_document:
            return format_html('<a href="{}" target="_blank" style="color: #3498db;">View ID</a>', obj.id_document.url)
        return "-"
    view_id.short_description = 'ID'

    def view_proof(self, obj):
        if obj.proof_of_address:
            return format_html('<a href="{}" target="_blank" style="color: #3498db;">View Proof</a>', obj.proof_of_address.url)
        return "-"
    view_proof.short_description = 'Address'

    @admin.action(description="Verify selected sellers")
    def approve_fica(self, request, queryset):
        queryset.update(is_fica_verified=True)
        self.message_user(request, "Selected sellers are now verified.")

    @admin.action(description="Reject/Reset FICA status")
    def reject_fica(self, request, queryset):
        queryset.update(is_fica_verified=False, fica_submitted_at=None)
        self.message_user(request, "FICA status reset for selected users.")

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'seller', 'price', 'is_approved', 'available', 'created']
    list_filter = ['is_approved', 'available', 'category', 'created']
    list_editable = ['is_approved', 'available', 'price']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name', 'description']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['transaction_ref', 'full_name', 'total_price', 'paid', 'created_at']
    list_filter = ['paid', 'created_at']
    readonly_fields = ['transaction_ref', 'total_price', 'created_at']

