from django import forms
from .models import Review, Product

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'review']
        widgets = {
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 5}),
            'review': forms.Textarea(attrs={'rows': 3}),
        }



class SellerProductForm(forms.ModelForm):
    class Meta:
        model = Product
        exclude = ['seller', 'created_at', 'updated_at']