from django.shortcuts import render
from django.db.models import Count
from .models import Category


def category_list(request):
    """Display all categories with recipe counts."""
    categories = Category.objects.annotate(
        recipe_count=Count('recipes')
    ).order_by('name')

    search_query = request.GET.get('q', '').strip()

    if search_query:
        categories = categories.filter(name__icontains=search_query)

    context = {
        'categories': categories,
        'search_query': search_query,
    }
    return render(request, 'categories/category_list.html', context)


