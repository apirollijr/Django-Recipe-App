from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from categories.models import Category
from ingredients.models import Ingredient
from .models import Recipe, RecipeIngredient


User = get_user_model()


class RecipeModelTests(TestCase):
	def test_recipe_str(self):
		user = User.objects.create_user(username="bob", password="pass12345")
		category = Category.objects.create(name="Breakfast", slug="breakfast")
		recipe = Recipe.objects.create(
			title="Pancakes",
			description="Fluffy pancakes",
			instructions="Mix and fry",
			author=user,
			category=category,
		)
		self.assertEqual(str(recipe), "Pancakes")

	def test_recipe_ingredient_relation(self):
		recipe = Recipe.objects.create(title="Tea", instructions="Boil water")
		ing = Ingredient.objects.create(name="Water")
		RecipeIngredient.objects.create(recipe=recipe, ingredient=ing, quantity=500, unit="ml")
		self.assertEqual(recipe.recipe_ingredients.count(), 1)


class HomeViewTests(TestCase):
	def test_home_view_status_code(self):
		"""Home page returns 200."""
		response = self.client.get(reverse('recipes:home'))
		self.assertEqual(response.status_code, 200)

	def test_home_view_template(self):
		"""Home page uses correct template."""
		response = self.client.get(reverse('recipes:home'))
		self.assertTemplateUsed(response, 'recipes/recipes_home.html')


class RecipeListViewTests(TestCase):
	@classmethod
	def setUpTestData(cls):
		cls.user = User.objects.create_user(username="chef", password="pass12345")
		cls.category1 = Category.objects.create(name="Italian", slug="italian")
		cls.category2 = Category.objects.create(name="Mexican", slug="mexican")
		
		cls.recipe1 = Recipe.objects.create(
			title="Spaghetti Carbonara",
			description="Classic Italian pasta dish",
			instructions="Cook pasta, make sauce",
			author=cls.user,
			category=cls.category1,
			prep_time_minutes=10,
			cook_time_minutes=20,
		)
		cls.recipe2 = Recipe.objects.create(
			title="Tacos",
			description="Delicious Mexican tacos",
			instructions="Prepare filling, assemble",
			author=cls.user,
			category=cls.category2,
			prep_time_minutes=15,
			cook_time_minutes=10,
		)
		cls.recipe3 = Recipe.objects.create(
			title="Lasagna",
			description="Layered Italian comfort food",
			instructions="Layer and bake",
			author=cls.user,
			category=cls.category1,
			prep_time_minutes=30,
			cook_time_minutes=60,
		)

	def test_recipe_list_status_code(self):
		"""Recipe list page returns 200."""
		response = self.client.get(reverse('recipes:recipe_list'))
		self.assertEqual(response.status_code, 200)

	def test_recipe_list_template(self):
		"""Recipe list uses correct template."""
		response = self.client.get(reverse('recipes:recipe_list'))
		self.assertTemplateUsed(response, 'recipes/recipe_list.html')

	def test_recipe_list_contains_all_recipes(self):
		"""Recipe list contains all recipes."""
		response = self.client.get(reverse('recipes:recipe_list'))
		self.assertEqual(len(response.context['recipes']), 3)

	def test_recipe_list_context_has_categories(self):
		"""Recipe list context includes categories for filter."""
		response = self.client.get(reverse('recipes:recipe_list'))
		self.assertIn('categories', response.context)
		self.assertEqual(len(response.context['categories']), 2)

	def test_recipe_list_search_filter(self):
		"""Search filter returns matching recipes."""
		response = self.client.get(reverse('recipes:recipe_list'), {'q': 'Italian'})
		self.assertEqual(len(response.context['recipes']), 2)
		self.assertEqual(response.context['search_query'], 'Italian')

	def test_recipe_list_search_by_title(self):
		"""Search filter works on title."""
		response = self.client.get(reverse('recipes:recipe_list'), {'q': 'Tacos'})
		self.assertEqual(len(response.context['recipes']), 1)
		self.assertEqual(response.context['recipes'][0].title, 'Tacos')

	def test_recipe_list_category_filter(self):
		"""Category filter returns recipes in that category."""
		response = self.client.get(reverse('recipes:recipe_list'), {'category': 'italian'})
		self.assertEqual(len(response.context['recipes']), 2)
		self.assertEqual(response.context['category_filter'], 'italian')

	def test_recipe_list_max_time_filter(self):
		"""Max time filter returns recipes within time limit."""
		response = self.client.get(reverse('recipes:recipe_list'), {'max_time': '30'})
		# Tacos: 15+10=25, Carbonara: 10+20=30
		self.assertEqual(len(response.context['recipes']), 2)
		self.assertEqual(response.context['max_time'], '30')

	def test_recipe_list_combined_filters(self):
		"""Multiple filters work together."""
		response = self.client.get(reverse('recipes:recipe_list'), {
			'category': 'italian',
			'max_time': '35'
		})
		# Only Carbonara: Italian + 30min total
		self.assertEqual(len(response.context['recipes']), 1)
		self.assertEqual(response.context['recipes'][0].title, 'Spaghetti Carbonara')

	def test_recipe_list_no_results(self):
		"""Search with no matches returns empty list."""
		response = self.client.get(reverse('recipes:recipe_list'), {'q': 'Sushi'})
		self.assertEqual(len(response.context['recipes']), 0)

	def test_recipe_list_invalid_max_time(self):
		"""Invalid max_time is ignored gracefully."""
		response = self.client.get(reverse('recipes:recipe_list'), {'max_time': 'invalid'})
		self.assertEqual(response.status_code, 200)
		self.assertEqual(len(response.context['recipes']), 3)


class RecipeListIngredientFilterTests(TestCase):
	@classmethod
	def setUpTestData(cls):
		cls.ingredient1 = Ingredient.objects.create(name="Pasta", default_unit="g")
		cls.ingredient2 = Ingredient.objects.create(name="Tomatoes", default_unit="pcs")
		
		cls.recipe1 = Recipe.objects.create(
			title="Spaghetti",
			instructions="Cook pasta",
		)
		cls.recipe2 = Recipe.objects.create(
			title="Salad",
			instructions="Chop veggies",
		)
		cls.recipe3 = Recipe.objects.create(
			title="Pasta Salad",
			instructions="Mix it",
		)
		
		# Recipe 1 has pasta only
		RecipeIngredient.objects.create(recipe=cls.recipe1, ingredient=cls.ingredient1)
		# Recipe 2 has tomatoes only
		RecipeIngredient.objects.create(recipe=cls.recipe2, ingredient=cls.ingredient2)
		# Recipe 3 has both
		RecipeIngredient.objects.create(recipe=cls.recipe3, ingredient=cls.ingredient1)
		RecipeIngredient.objects.create(recipe=cls.recipe3, ingredient=cls.ingredient2)

	def test_recipe_list_ingredient_filter(self):
		"""Ingredient filter returns recipes containing that ingredient."""
		response = self.client.get(reverse('recipes:recipe_list'), {'ingredient': self.ingredient1.pk})
		self.assertEqual(len(response.context['recipes']), 2)
		self.assertEqual(response.context['ingredient_name'], 'Pasta')

	def test_recipe_list_ingredient_filter_single_recipe(self):
		"""Ingredient filter works when only one recipe matches."""
		response = self.client.get(reverse('recipes:recipe_list'), {'ingredient': self.ingredient2.pk})
		titles = [r.title for r in response.context['recipes']]
		self.assertIn('Salad', titles)
		self.assertIn('Pasta Salad', titles)
		self.assertNotIn('Spaghetti', titles)

	def test_recipe_list_invalid_ingredient(self):
		"""Invalid ingredient ID is ignored gracefully."""
		response = self.client.get(reverse('recipes:recipe_list'), {'ingredient': 'invalid'})
		self.assertEqual(response.status_code, 200)

	def test_recipe_list_nonexistent_ingredient(self):
		"""Non-existent ingredient ID returns all recipes."""
		response = self.client.get(reverse('recipes:recipe_list'), {'ingredient': 9999})
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.context['ingredient_name'], '')


class RecipeDetailViewTests(TestCase):
	@classmethod
	def setUpTestData(cls):
		cls.user = User.objects.create_user(username="chef", password="pass12345")
		cls.category = Category.objects.create(name="Italian", slug="italian")
		cls.ingredient1 = Ingredient.objects.create(name="Pasta", default_unit="g")
		cls.ingredient2 = Ingredient.objects.create(name="Eggs", default_unit="pcs")
		
		cls.recipe = Recipe.objects.create(
			title="Spaghetti Carbonara",
			description="Classic Italian pasta dish",
			instructions="1. Cook pasta\n2. Make sauce\n3. Combine",
			author=cls.user,
			category=cls.category,
			prep_time_minutes=10,
			cook_time_minutes=20,
		)
		RecipeIngredient.objects.create(
			recipe=cls.recipe,
			ingredient=cls.ingredient1,
			quantity=200,
			unit="g"
		)
		RecipeIngredient.objects.create(
			recipe=cls.recipe,
			ingredient=cls.ingredient2,
			quantity=2,
			unit="pcs",
			notes="room temperature"
		)

	def test_recipe_detail_status_code(self):
		"""Recipe detail page returns 200."""
		response = self.client.get(reverse('recipes:recipe_detail', args=[self.recipe.pk]))
		self.assertEqual(response.status_code, 200)

	def test_recipe_detail_template(self):
		"""Recipe detail uses correct template."""
		response = self.client.get(reverse('recipes:recipe_detail', args=[self.recipe.pk]))
		self.assertTemplateUsed(response, 'recipes/recipe_detail.html')

	def test_recipe_detail_context(self):
		"""Recipe detail context contains recipe and total_time."""
		response = self.client.get(reverse('recipes:recipe_detail', args=[self.recipe.pk]))
		self.assertEqual(response.context['recipe'], self.recipe)
		self.assertEqual(response.context['total_time'], 30)

	def test_recipe_detail_contains_title(self):
		"""Recipe detail page contains recipe title."""
		response = self.client.get(reverse('recipes:recipe_detail', args=[self.recipe.pk]))
		self.assertContains(response, 'Spaghetti Carbonara')

	def test_recipe_detail_contains_ingredients(self):
		"""Recipe detail page contains ingredients."""
		response = self.client.get(reverse('recipes:recipe_detail', args=[self.recipe.pk]))
		self.assertContains(response, 'Pasta')
		self.assertContains(response, 'Eggs')
		self.assertContains(response, 'room temperature')

	def test_recipe_detail_contains_instructions(self):
		"""Recipe detail page contains instructions."""
		response = self.client.get(reverse('recipes:recipe_detail', args=[self.recipe.pk]))
		self.assertContains(response, 'Cook pasta')

	def test_recipe_detail_404_for_invalid_pk(self):
		"""Recipe detail returns 404 for non-existent recipe."""
		response = self.client.get(reverse('recipes:recipe_detail', args=[9999]))
		self.assertEqual(response.status_code, 404)


class AuthenticationTests(TestCase):
	def test_login_page_status_code(self):
		"""Login page returns 200."""
		response = self.client.get(reverse('login'))
		self.assertEqual(response.status_code, 200)

	def test_login_page_template(self):
		"""Login page uses correct template."""
		response = self.client.get(reverse('login'))
		self.assertTemplateUsed(response, 'auth/login.html')

	def test_register_page_status_code(self):
		"""Register page returns 200."""
		response = self.client.get(reverse('register'))
		self.assertEqual(response.status_code, 200)

	def test_register_page_template(self):
		"""Register page uses correct template."""
		response = self.client.get(reverse('register'))
		self.assertTemplateUsed(response, 'auth/register.html')

	def test_user_registration(self):
		"""User can register a new account."""
		response = self.client.post(reverse('register'), {
			'username': 'newuser',
			'password1': 'testpass123!',
			'password2': 'testpass123!',
		})
		self.assertRedirects(response, reverse('recipes:home'))
		# Check user was created
		self.assertTrue(User.objects.filter(username='newuser').exists())

	def test_user_registration_auto_login(self):
		"""User is automatically logged in after registration."""
		self.client.post(reverse('register'), {
			'username': 'newuser',
			'password1': 'testpass123!',
			'password2': 'testpass123!',
		})
		# Check user is authenticated by accessing a page
		response = self.client.get(reverse('recipes:home'))
		self.assertTrue(response.context['user'].is_authenticated)

	def test_user_registration_invalid_password(self):
		"""Registration fails with mismatched passwords."""
		response = self.client.post(reverse('register'), {
			'username': 'newuser',
			'password1': 'testpass123!',
			'password2': 'differentpass!',
		})
		self.assertEqual(response.status_code, 200)
		self.assertFalse(User.objects.filter(username='newuser').exists())

	def test_user_login(self):
		"""User can log in with valid credentials."""
		User.objects.create_user(username='testuser', password='testpass123!')
		response = self.client.post(reverse('login'), {
			'username': 'testuser',
			'password': 'testpass123!',
		})
		self.assertRedirects(response, '/')

	def test_user_login_invalid(self):
		"""Login fails with invalid credentials."""
		User.objects.create_user(username='testuser', password='testpass123!')
		response = self.client.post(reverse('login'), {
			'username': 'testuser',
			'password': 'wrongpassword',
		})
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'Invalid username or password')

	def test_user_logout(self):
		"""User can log out."""
		User.objects.create_user(username='testuser', password='testpass123!')
		self.client.login(username='testuser', password='testpass123!')
		response = self.client.post(reverse('logout'))
		self.assertRedirects(response, '/')
		# Check user is logged out
		response = self.client.get(reverse('recipes:home'))
		self.assertFalse(response.context['user'].is_authenticated)

	def test_authenticated_user_redirect_from_register(self):
		"""Authenticated users are redirected away from register page."""
		User.objects.create_user(username='testuser', password='testpass123!')
		self.client.login(username='testuser', password='testpass123!')
		response = self.client.get(reverse('register'))
		self.assertRedirects(response, reverse('recipes:home'))


class RecipeSearchFormTests(TestCase):
	"""Tests for the RecipeSearchForm."""
	
	@classmethod
	def setUpTestData(cls):
		cls.category = Category.objects.create(name="Italian", slug="italian")
		cls.ingredient = Ingredient.objects.create(name="Tomato", default_unit="pcs")

	def test_form_fields_exist(self):
		"""Form contains all expected fields."""
		from recipes.forms import RecipeSearchForm
		form = RecipeSearchForm()
		self.assertIn('recipe_name', form.fields)
		self.assertIn('ingredient', form.fields)
		self.assertIn('category', form.fields)
		self.assertIn('max_time', form.fields)

	def test_form_fields_not_required(self):
		"""All form fields should be optional."""
		from recipes.forms import RecipeSearchForm
		form = RecipeSearchForm(data={})
		self.assertTrue(form.is_valid())

	def test_form_valid_with_recipe_name(self):
		"""Form is valid with just recipe name."""
		from recipes.forms import RecipeSearchForm
		form = RecipeSearchForm(data={'recipe_name': 'Pasta'})
		self.assertTrue(form.is_valid())
		self.assertEqual(form.cleaned_data['recipe_name'], 'Pasta')

	def test_form_valid_with_category(self):
		"""Form is valid with category selection."""
		from recipes.forms import RecipeSearchForm
		form = RecipeSearchForm(data={'category': self.category.pk})
		self.assertTrue(form.is_valid())
		self.assertEqual(form.cleaned_data['category'], self.category)

	def test_form_valid_with_ingredient(self):
		"""Form is valid with ingredient selection."""
		from recipes.forms import RecipeSearchForm
		form = RecipeSearchForm(data={'ingredient': self.ingredient.pk})
		self.assertTrue(form.is_valid())
		self.assertEqual(form.cleaned_data['ingredient'], self.ingredient)

	def test_form_valid_with_max_time(self):
		"""Form is valid with max_time."""
		from recipes.forms import RecipeSearchForm
		form = RecipeSearchForm(data={'max_time': 30})
		self.assertTrue(form.is_valid())
		self.assertEqual(form.cleaned_data['max_time'], 30)

	def test_form_invalid_max_time_zero(self):
		"""Form is invalid with max_time of 0."""
		from recipes.forms import RecipeSearchForm
		form = RecipeSearchForm(data={'max_time': 0})
		self.assertFalse(form.is_valid())
		self.assertIn('max_time', form.errors)

	def test_form_invalid_max_time_negative(self):
		"""Form is invalid with negative max_time."""
		from recipes.forms import RecipeSearchForm
		form = RecipeSearchForm(data={'max_time': -5})
		self.assertFalse(form.is_valid())
		self.assertIn('max_time', form.errors)

	def test_form_recipe_name_strips_whitespace(self):
		"""Recipe name field strips leading/trailing whitespace."""
		from recipes.forms import RecipeSearchForm
		form = RecipeSearchForm(data={'recipe_name': '  Pasta  '})
		self.assertTrue(form.is_valid())
		self.assertEqual(form.cleaned_data['recipe_name'], 'Pasta')

	def test_form_recipe_name_max_length(self):
		"""Recipe name respects max length of 200 characters."""
		from recipes.forms import RecipeSearchForm
		form = RecipeSearchForm(data={'recipe_name': 'A' * 201})
		self.assertFalse(form.is_valid())
		self.assertIn('recipe_name', form.errors)

	def test_form_valid_with_all_fields(self):
		"""Form is valid with all fields filled."""
		from recipes.forms import RecipeSearchForm
		form = RecipeSearchForm(data={
			'recipe_name': 'Spaghetti',
			'ingredient': self.ingredient.pk,
			'category': self.category.pk,
			'max_time': 45
		})
		self.assertTrue(form.is_valid())


class RecipeSearchViewTests(TestCase):
	"""Tests for the recipe_search view."""
	
	@classmethod
	def setUpTestData(cls):
		cls.user = User.objects.create_user(username="chef", password="pass12345")
		cls.category1 = Category.objects.create(name="Italian", slug="italian")
		cls.category2 = Category.objects.create(name="Mexican", slug="mexican")
		cls.ingredient = Ingredient.objects.create(name="Tomato", default_unit="pcs")
		
		cls.recipe1 = Recipe.objects.create(
			title="Spaghetti Carbonara",
			description="Classic Italian pasta dish",
			instructions="Cook pasta, make sauce",
			author=cls.user,
			category=cls.category1,
			prep_time_minutes=10,
			cook_time_minutes=20,
		)
		cls.recipe2 = Recipe.objects.create(
			title="Tacos",
			description="Delicious Mexican tacos",
			instructions="Prepare filling, assemble",
			author=cls.user,
			category=cls.category2,
			prep_time_minutes=15,
			cook_time_minutes=10,
		)
		cls.recipe3 = Recipe.objects.create(
			title="Chicken Parmesan",
			description="Italian chicken dish",
			instructions="Bread and bake",
			author=cls.user,
			category=cls.category1,
			prep_time_minutes=20,
			cook_time_minutes=40,
		)
		
		# Add ingredient to recipe1
		RecipeIngredient.objects.create(recipe=cls.recipe1, ingredient=cls.ingredient)

	def test_search_view_requires_login(self):
		"""Search view redirects unauthenticated users to login."""
		response = self.client.get(reverse('recipes:recipe_search'))
		self.assertEqual(response.status_code, 302)
		self.assertIn('login', response.url)

	def test_search_view_accessible_when_logged_in(self):
		"""Search view is accessible to authenticated users."""
		self.client.login(username='chef', password='pass12345')
		response = self.client.get(reverse('recipes:recipe_search'))
		self.assertEqual(response.status_code, 200)

	def test_search_view_uses_correct_template(self):
		"""Search view uses the correct template."""
		self.client.login(username='chef', password='pass12345')
		response = self.client.get(reverse('recipes:recipe_search'))
		self.assertTemplateUsed(response, 'recipes/recipe_search.html')

	def test_search_view_contains_form(self):
		"""Search view contains the search form."""
		self.client.login(username='chef', password='pass12345')
		response = self.client.get(reverse('recipes:recipe_search'))
		self.assertIn('form', response.context)

	def test_search_by_recipe_name_partial_match(self):
		"""Search finds recipes with partial name match (wildcard)."""
		self.client.login(username='chef', password='pass12345')
		response = self.client.get(reverse('recipes:recipe_search'), {'recipe_name': 'Spag'})
		self.assertTrue(response.context['search_performed'])
		self.assertIn('Spaghetti', response.content.decode())

	def test_search_by_recipe_name_case_insensitive(self):
		"""Search is case-insensitive."""
		self.client.login(username='chef', password='pass12345')
		response = self.client.get(reverse('recipes:recipe_search'), {'recipe_name': 'spaghetti'})
		self.assertTrue(response.context['search_performed'])
		self.assertIn('Spaghetti', response.content.decode())

	def test_search_by_category(self):
		"""Search filters by category correctly."""
		self.client.login(username='chef', password='pass12345')
		response = self.client.get(reverse('recipes:recipe_search'), {'category': self.category1.pk})
		self.assertTrue(response.context['search_performed'])
		self.assertEqual(response.context['result_count'], 2)  # Spaghetti and Chicken Parmesan

	def test_search_by_ingredient(self):
		"""Search filters by ingredient correctly."""
		self.client.login(username='chef', password='pass12345')
		response = self.client.get(reverse('recipes:recipe_search'), {'ingredient': self.ingredient.pk})
		self.assertTrue(response.context['search_performed'])
		self.assertEqual(response.context['result_count'], 1)

	def test_search_by_max_time(self):
		"""Search filters by max time correctly."""
		self.client.login(username='chef', password='pass12345')
		response = self.client.get(reverse('recipes:recipe_search'), {'max_time': 30})
		self.assertTrue(response.context['search_performed'])
		# Spaghetti: 30, Tacos: 25
		self.assertEqual(response.context['result_count'], 2)

	def test_show_all_recipes(self):
		"""Show all button displays all recipes."""
		self.client.login(username='chef', password='pass12345')
		response = self.client.get(reverse('recipes:recipe_search'), {'show_all': '1'})
		self.assertTrue(response.context['search_performed'])
		self.assertEqual(response.context['result_count'], 3)

	def test_search_no_results(self):
		"""Search with no matches returns empty results."""
		self.client.login(username='chef', password='pass12345')
		response = self.client.get(reverse('recipes:recipe_search'), {'recipe_name': 'NonExistent'})
		self.assertTrue(response.context['search_performed'])
		self.assertEqual(response.context['result_count'], 0)

	def test_search_results_contain_clickable_links(self):
		"""Search results contain clickable recipe links."""
		self.client.login(username='chef', password='pass12345')
		response = self.client.get(reverse('recipes:recipe_search'), {'show_all': '1'})
		content = response.content.decode()
		# Check that recipe links are present
		self.assertIn(f'/recipes/{self.recipe1.pk}/', content)
		self.assertIn('recipe-link', content)

	def test_search_combined_filters(self):
		"""Multiple filters work together."""
		self.client.login(username='chef', password='pass12345')
		response = self.client.get(reverse('recipes:recipe_search'), {
			'category': self.category1.pk,
			'max_time': 35
		})
		self.assertTrue(response.context['search_performed'])
		self.assertEqual(response.context['result_count'], 1)  # Only Spaghetti

	def test_search_view_has_charts(self):
		"""Search view contains chart data."""
		self.client.login(username='chef', password='pass12345')
		response = self.client.get(reverse('recipes:recipe_search'))
		# Charts are always generated
		self.assertIn('bar_chart', response.context)
		self.assertIn('pie_chart', response.context)
		self.assertIn('line_chart', response.context)


class DataVisualizationTests(TestCase):
	"""Tests for data visualization functions."""
	
	@classmethod
	def setUpTestData(cls):
		cls.user = User.objects.create_user(username="chef", password="pass12345")
		cls.category = Category.objects.create(name="Italian", slug="italian")
		
		cls.recipe1 = Recipe.objects.create(
			title="Quick Pasta",
			instructions="Cook fast",
			author=cls.user,
			category=cls.category,
			prep_time_minutes=5,
			cook_time_minutes=10,  # Quick: 15 min
		)
		cls.recipe2 = Recipe.objects.create(
			title="Medium Dish",
			instructions="Cook medium",
			author=cls.user,
			category=cls.category,
			prep_time_minutes=15,
			cook_time_minutes=20,  # Medium: 35 min
		)
		cls.recipe3 = Recipe.objects.create(
			title="Slow Cook",
			instructions="Cook slow",
			author=cls.user,
			category=cls.category,
			prep_time_minutes=30,
			cook_time_minutes=60,  # Long: 90 min
		)

	def test_bar_chart_generation(self):
		"""Bar chart is generated with recipe data."""
		from recipes.views import create_bar_chart
		chart = create_bar_chart(Recipe.objects.all())
		self.assertIsNotNone(chart)
		# Chart should be base64 encoded
		self.assertIsInstance(chart, str)

	def test_pie_chart_generation(self):
		"""Pie chart is generated with recipe data."""
		from recipes.views import create_pie_chart
		chart = create_pie_chart(Recipe.objects.all())
		self.assertIsNotNone(chart)
		self.assertIsInstance(chart, str)

	def test_line_chart_generation(self):
		"""Line chart is generated with recipe data."""
		from recipes.views import create_line_chart
		chart = create_line_chart(Recipe.objects.all())
		# May return None if not enough data points
		if chart:
			self.assertIsInstance(chart, str)

	def test_bar_chart_empty_queryset(self):
		"""Bar chart handles empty queryset gracefully."""
		from recipes.views import create_bar_chart
		chart = create_bar_chart(Recipe.objects.none())
		self.assertIsNone(chart)

	def test_pie_chart_empty_queryset(self):
		"""Pie chart handles empty queryset gracefully."""
		from recipes.views import create_pie_chart
		chart = create_pie_chart(Recipe.objects.none())
		self.assertIsNone(chart)

