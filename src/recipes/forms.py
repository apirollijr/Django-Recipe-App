from django import forms
from categories.models import Category
from ingredients.models import Ingredient


class RecipeSearchForm(forms.Form):
    """Form for searching recipes with various filters."""
    
    recipe_name = forms.CharField(
        max_length=200,
        required=False,
        label='Recipe Name',
        widget=forms.TextInput(attrs={
            'placeholder': 'Search by name (e.g., "chicken", "pasta")',
            'class': 'form-control'
        })
    )
    
    ingredient = forms.ModelChoiceField(
        queryset=Ingredient.objects.all().order_by('name'),
        required=False,
        empty_label='All Ingredients',
        label='Ingredient',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    category = forms.ModelChoiceField(
        queryset=Category.objects.all().order_by('name'),
        required=False,
        empty_label='All Categories',
        label='Category',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    max_time = forms.IntegerField(
        required=False,
        min_value=1,
        label='Max Total Time (minutes)',
        widget=forms.NumberInput(attrs={
            'placeholder': 'e.g., 30',
            'class': 'form-control',
            'min': '1'
        })
    )

    def clean_recipe_name(self):
        """Clean and validate the recipe name field."""
        name = self.cleaned_data.get('recipe_name', '')
        return name.strip() if name else ''

    def clean_max_time(self):
        """Ensure max_time is a positive integer."""
        max_time = self.cleaned_data.get('max_time')
        if max_time is not None and max_time < 1:
            raise forms.ValidationError('Maximum time must be at least 1 minute.')
        return max_time
