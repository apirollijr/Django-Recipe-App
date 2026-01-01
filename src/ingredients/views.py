from django.shortcuts import render
from django.db.models import Count
from .models import Ingredient


def ingredient_list(request):
    """Display all ingredients with recipe counts."""
    ingredients = Ingredient.objects.annotate(
        recipe_count=Count('ingredient_recipes')
    ).order_by('name')

    search_query = request.GET.get('q', '').strip()

    if search_query:
        ingredients = ingredients.filter(name__icontains=search_query)

    context = {
        'ingredients': ingredients,
        'search_query': search_query,
    }
    return render(request, 'ingredients/ingredient_list.html', context)

