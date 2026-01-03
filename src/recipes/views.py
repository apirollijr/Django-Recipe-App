from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q, Count, F
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Recipe
from .forms import RecipeSearchForm
from categories.models import Category
from ingredients.models import Ingredient
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from datetime import datetime
from collections import Counter


def home(request):
	return render(request, 'recipes/recipes_home.html')


def register(request):
	"""Handle user registration."""
	if request.user.is_authenticated:
		return redirect('recipes:home')
	
	if request.method == 'POST':
		form = UserCreationForm(request.POST)
		if form.is_valid():
			user = form.save()
			login(request, user)
			messages.success(request, f'Welcome, {user.username}! Your account has been created.')
			return redirect('recipes:home')
	else:
		form = UserCreationForm()
	
	return render(request, 'auth/register.html', {'form': form})


def recipe_list(request):
	"""Display all recipes with optional filtering."""
	recipes = Recipe.objects.select_related('category', 'author').all()
	categories = Category.objects.all()

	# Get filter parameters
	search_query = request.GET.get('q', '').strip()
	category_filter = request.GET.get('category', '')
	ingredient_filter = request.GET.get('ingredient', '')
	max_time = request.GET.get('max_time', '')

	# For displaying ingredient name if filtered
	ingredient_name = ''

	# Apply search filter (title or description)
	if search_query:
		recipes = recipes.filter(
			Q(title__icontains=search_query) | Q(description__icontains=search_query)
		)

	# Apply category filter
	if category_filter:
		recipes = recipes.filter(category__slug=category_filter)

	# Apply ingredient filter
	if ingredient_filter:
		try:
			ingredient_id = int(ingredient_filter)
			ingredient = Ingredient.objects.filter(pk=ingredient_id).first()
			if ingredient:
				ingredient_name = ingredient.name
				recipes = recipes.filter(recipe_ingredients__ingredient_id=ingredient_id)
		except ValueError:
			pass

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
		'ingredient_filter': ingredient_filter,
		'ingredient_name': ingredient_name,
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


def get_chart_base64(fig):
	"""Convert a matplotlib figure to base64 encoded string."""
	buffer = BytesIO()
	fig.savefig(buffer, format='png', bbox_inches='tight', dpi=100)
	buffer.seek(0)
	image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
	buffer.close()
	plt.close(fig)
	return image_base64


def create_bar_chart(recipes_qs):
	"""Create a bar chart showing recipes per category."""
	# Count recipes per category
	category_counts = recipes_qs.values('category__name').annotate(
		count=Count('id')
	).order_by('-count')
	
	categories = [item['category__name'] or 'Uncategorized' for item in category_counts]
	counts = [item['count'] for item in category_counts]
	
	if not categories:
		return None
	
	fig, ax = plt.subplots(figsize=(10, 6))
	bars = ax.bar(categories, counts, color='#4f8cff', edgecolor='#3a6fd8')
	
	# Add value labels on bars
	for bar, count in zip(bars, counts):
		ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
				str(count), ha='center', va='bottom', fontweight='bold')
	
	ax.set_xlabel('Category', fontsize=12)
	ax.set_ylabel('Number of Recipes', fontsize=12)
	ax.set_title('Recipes per Category', fontsize=14, fontweight='bold')
	plt.xticks(rotation=45, ha='right')
	plt.tight_layout()
	
	return get_chart_base64(fig)


def create_pie_chart(recipes_qs):
	"""Create a pie chart showing recipe distribution by cooking time difficulty."""
	# Categorize recipes by total time
	quick = 0  # <= 15 min
	medium = 0  # 16-45 min
	long_time = 0  # > 45 min
	
	for recipe in recipes_qs:
		total = recipe.prep_time_minutes + recipe.cook_time_minutes
		if total <= 15:
			quick += 1
		elif total <= 45:
			medium += 1
		else:
			long_time += 1
	
	labels = ['Quick (≤15 min)', 'Medium (16-45 min)', 'Long (>45 min)']
	sizes = [quick, medium, long_time]
	colors = ['#4ade80', '#facc15', '#f87171']
	
	# Filter out zero values
	filtered_data = [(l, s, c) for l, s, c in zip(labels, sizes, colors) if s > 0]
	if not filtered_data:
		return None
	
	labels, sizes, colors = zip(*filtered_data)
	
	fig, ax = plt.subplots(figsize=(8, 8))
	wedges, texts, autotexts = ax.pie(
		sizes, labels=labels, colors=colors, autopct='%1.1f%%',
		startangle=90, explode=[0.02] * len(sizes)
	)
	
	for autotext in autotexts:
		autotext.set_fontsize(11)
		autotext.set_fontweight('bold')
	
	ax.set_title('Recipe Distribution by Time Complexity', fontsize=14, fontweight='bold')
	plt.tight_layout()
	
	return get_chart_base64(fig)


def create_line_chart(recipes_qs):
	"""Create a line chart showing cumulative recipes over time."""
	# Get recipes with dates
	recipes_with_dates = recipes_qs.filter(created_at__isnull=False).order_by('created_at')
	
	if not recipes_with_dates.exists():
		return None
	
	dates = []
	cumulative_counts = []
	count = 0
	
	for recipe in recipes_with_dates:
		count += 1
		dates.append(recipe.created_at)
		cumulative_counts.append(count)
	
	if len(dates) < 2:
		return None
	
	fig, ax = plt.subplots(figsize=(10, 6))
	ax.plot(dates, cumulative_counts, marker='o', color='#4f8cff', linewidth=2, markersize=6)
	ax.fill_between(dates, cumulative_counts, alpha=0.3, color='#4f8cff')
	
	ax.set_xlabel('Date', fontsize=12)
	ax.set_ylabel('Cumulative Recipes', fontsize=12)
	ax.set_title('Recipe Collection Growth Over Time', fontsize=14, fontweight='bold')
	plt.xticks(rotation=45, ha='right')
	ax.grid(True, alpha=0.3)
	plt.tight_layout()
	
	return get_chart_base64(fig)


@login_required
def recipe_search(request):
	"""Search recipes with filters and display results as pandas DataFrame table."""
	form = RecipeSearchForm(request.GET or None)
	recipes_df = None
	search_performed = False
	show_all = request.GET.get('show_all', False)
	
	# Get base queryset
	recipes = Recipe.objects.select_related('category', 'author').prefetch_related(
		'recipe_ingredients__ingredient'
	)
	
	if show_all:
		search_performed = True
	elif form.is_valid() and any([
		form.cleaned_data.get('recipe_name'),
		form.cleaned_data.get('ingredient'),
		form.cleaned_data.get('category'),
		form.cleaned_data.get('max_time')
	]):
		search_performed = True
		
		# Apply recipe name filter with partial matching (wildcard/icontains)
		recipe_name = form.cleaned_data.get('recipe_name')
		if recipe_name:
			# Split search terms for flexible matching
			search_terms = recipe_name.split()
			query = Q()
			for term in search_terms:
				query |= Q(title__icontains=term) | Q(description__icontains=term)
			recipes = recipes.filter(query)
		
		# Apply ingredient filter
		ingredient = form.cleaned_data.get('ingredient')
		if ingredient:
			recipes = recipes.filter(recipe_ingredients__ingredient=ingredient)
		
		# Apply category filter
		category = form.cleaned_data.get('category')
		if category:
			recipes = recipes.filter(category=category)
		
		# Apply max time filter
		max_time = form.cleaned_data.get('max_time')
		if max_time:
			recipes = recipes.annotate(
				total_time=F('prep_time_minutes') + F('cook_time_minutes')
			).filter(total_time__lte=max_time)
	
	recipes = recipes.distinct().order_by('-created_at')
	
	# Convert to pandas DataFrame if search was performed
	if search_performed and recipes.exists():
		data = []
		for recipe in recipes:
			ingredient_count = recipe.recipe_ingredients.count()
			total_time = recipe.prep_time_minutes + recipe.cook_time_minutes
			data.append({
				'id': recipe.pk,
				'name': recipe.title,
				'category': recipe.category.name if recipe.category else 'Uncategorized',
				'ingredients': ingredient_count,
				'total_time': f"{total_time} min",
				'author': recipe.author.username if recipe.author else 'Unknown'
			})
		
		df = pd.DataFrame(data)
		recipes_df = df.to_html(
			classes='search-results-table',
			index=False,
			escape=False,
			columns=['name', 'category', 'ingredients', 'total_time', 'author']
		)
		
		# Make recipe names clickable
		for recipe in recipes:
			old_name = f'<td>{recipe.title}</td>'
			new_name = f'<td><a href="/recipes/{recipe.pk}/" class="recipe-link">{recipe.title}</a></td>'
			recipes_df = recipes_df.replace(old_name, new_name)
	
	# Generate charts
	all_recipes = Recipe.objects.all()
	bar_chart = create_bar_chart(all_recipes)
	pie_chart = create_pie_chart(all_recipes)
	line_chart = create_line_chart(all_recipes)
	
	context = {
		'form': form,
		'recipes_df': recipes_df,
		'search_performed': search_performed,
		'result_count': recipes.count() if search_performed else 0,
		'bar_chart': bar_chart,
		'pie_chart': pie_chart,
		'line_chart': line_chart,
	}
	
	return render(request, 'recipes/recipe_search.html', context)

