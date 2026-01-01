from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Recipe
from categories.models import Category


def home(request):
	return render(request, 'recipes/recipes_home.html')


def recipe_list(request):
	"""Display all recipes with optional filtering."""
	recipes = Recipe.objects.select_related('category', 'author').all()
	categories = Category.objects.all()

	# Get filter parameters
	search_query = request.GET.get('q', '').strip()
	category_filter = request.GET.get('category', '')
	max_time = request.GET.get('max_time', '')

	# Apply search filter (title or description)
	if search_query:
		recipes = recipes.filter(
			Q(title__icontains=search_query) | Q(description__icontains=search_query)
		)

	# Apply category filter
	if category_filter:
		recipes = recipes.filter(category__slug=category_filter)

	# Apply max total time filter
	if max_time:
		try:
			max_minutes = int(max_time)
			# Filter where prep_time + cook_time <= max_minutes
			from django.db.models import F
			recipes = recipes.annotate(
				total_time=F('prep_time_minutes') + F('cook_time_minutes')
			).filter(total_time__lte=max_minutes)
		except ValueError:
			pass

	recipes = recipes.order_by('-created_at')

	context = {
		'recipes': recipes,
		'categories': categories,
		'search_query': search_query,
		'category_filter': category_filter,
		'max_time': max_time,
	}
	return render(request, 'recipes/recipe_list.html', context)


def recipe_detail(request, pk):
	"""Display a single recipe with full details."""
	recipe = get_object_or_404(
		Recipe.objects.select_related('category', 'author')
		.prefetch_related('recipe_ingredients__ingredient'),
		pk=pk
	)
	
	total_time = recipe.prep_time_minutes + recipe.cook_time_minutes
	
	context = {
		'recipe': recipe,
		'total_time': total_time,
	}
	return render(request, 'recipes/recipe_detail.html', context)
