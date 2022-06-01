from django import forms
from .models import Shopping

class ShoppingForm(forms.ModelForm):
    class Meta:
        model = Shopping
        # fields = '__all__'
        fields = ['item_name', 'item_price', 'quantity', 'tax_free_amount']

