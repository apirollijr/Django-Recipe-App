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
