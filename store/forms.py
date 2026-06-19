from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class CartAddProductForm(forms.Form):
    quantity = forms.IntegerField(
        min_value=1,
        max_value=99,
        widget=forms.TextInput(attrs={'style': 'width: 50px; text-align: center;'}),
        label=''
    )
    override = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.HiddenInput
    )

class SignUpForm(UserCreationForm):
    ROLE_CHOICES = [
        ('buyer', 'Register as Buyer'),
        ('seller', 'Register as Seller'),
    ]
    role = forms.ChoiceField(
        choices=ROLE_CHOICES, 
        widget=forms.RadioSelect,
        help_text="Choose how you want to use the store."
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email', 'first_name', 'last_name')

    def save(self, commit=True):
        user = super().save(commit=False)
        role = self.cleaned_data.get('role')
        if role == 'seller':
            user.is_seller = True
            user.is_buyer = False
        else:
            user.is_buyer = True
            user.is_seller = False
        if commit:
            user.save()
        return user


from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['category', 'name', 'image', 'description', 'price', 'available']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }


from django import forms
from .models import User

class FicaUploadForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['id_document', 'proof_of_address']
        help_texts = {
            'id_document': 'Upload a clear copy of your ID or Passport.',
            'proof_of_address': 'Utility bill or bank statement (not older than 3 months).',
        }


from django import forms
from .models import Order

class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['full_name', 'email', 'phone_number', 'address', 'city', 'province', 'postal_code']
        widgets = {
            'address': forms.TextInput(attrs={'placeholder': 'Street address and suburb'}),
            'phone_number': forms.TextInput(attrs={'placeholder': '081 234 5678'}),
        }

