from django.test import TestCase
from django.urls import reverse
from recipes.models import Recipe, RecipeIngredient
from .models import Ingredient


class IngredientModelTests(TestCase):
	def test_str(self):
		ing = Ingredient.objects.create(name="Sugar", default_unit="g")
		self.assertEqual(str(ing), "Sugar")


class IngredientListViewTests(TestCase):
	@classmethod
	def setUpTestData(cls):
		cls.ingredient1 = Ingredient.objects.create(name="Tomatoes", default_unit="pcs")
		cls.ingredient2 = Ingredient.objects.create(name="Onions", default_unit="pcs")
		cls.ingredient3 = Ingredient.objects.create(name="Garlic", default_unit="cloves")
		cls.ingredient4 = Ingredient.objects.create(name="Olive Oil", default_unit="ml")
		
		# Create recipes and link ingredients for count testing
		cls.recipe1 = Recipe.objects.create(title="Salsa", instructions="Blend it")
		cls.recipe2 = Recipe.objects.create(title="Soup", instructions="Boil it")
		
		RecipeIngredient.objects.create(recipe=cls.recipe1, ingredient=cls.ingredient1)
		RecipeIngredient.objects.create(recipe=cls.recipe1, ingredient=cls.ingredient2)
		RecipeIngredient.objects.create(recipe=cls.recipe1, ingredient=cls.ingredient3)
		RecipeIngredient.objects.create(recipe=cls.recipe2, ingredient=cls.ingredient1)
		RecipeIngredient.objects.create(recipe=cls.recipe2, ingredient=cls.ingredient2)

	def test_ingredient_list_status_code(self):
		"""Ingredient list page returns 200."""
		response = self.client.get(reverse('ingredients:ingredient_list'))
		self.assertEqual(response.status_code, 200)

	def test_ingredient_list_template(self):
		"""Ingredient list uses correct template."""
		response = self.client.get(reverse('ingredients:ingredient_list'))
		self.assertTemplateUsed(response, 'ingredients/ingredient_list.html')

	def test_ingredient_list_contains_all_ingredients(self):
		"""Ingredient list contains all ingredients."""
		response = self.client.get(reverse('ingredients:ingredient_list'))
		self.assertEqual(len(response.context['ingredients']), 4)

	def test_ingredient_list_has_recipe_counts(self):
		"""Ingredients have correct recipe counts."""
		response = self.client.get(reverse('ingredients:ingredient_list'))
		ingredients = {i.name: i for i in response.context['ingredients']}
		self.assertEqual(ingredients['Tomatoes'].recipe_count, 2)
		self.assertEqual(ingredients['Onions'].recipe_count, 2)
		self.assertEqual(ingredients['Garlic'].recipe_count, 1)
		self.assertEqual(ingredients['Olive Oil'].recipe_count, 0)

	def test_ingredient_list_search_filter(self):
		"""Search filter returns matching ingredients."""
		response = self.client.get(reverse('ingredients:ingredient_list'), {'q': 'Tomatoes'})
		self.assertEqual(len(response.context['ingredients']), 1)
		self.assertEqual(response.context['ingredients'][0].name, 'Tomatoes')
		self.assertEqual(response.context['search_query'], 'Tomatoes')

	def test_ingredient_list_search_partial_match(self):
		"""Search filter works with partial matches."""
		response = self.client.get(reverse('ingredients:ingredient_list'), {'q': 'on'})
		# Matches Onions
		self.assertEqual(len(response.context['ingredients']), 1)

	def test_ingredient_list_search_no_results(self):
		"""Search with no matches returns empty list."""
		response = self.client.get(reverse('ingredients:ingredient_list'), {'q': 'Butter'})
		self.assertEqual(len(response.context['ingredients']), 0)

	def test_ingredient_list_search_case_insensitive(self):
		"""Search is case insensitive."""
		response = self.client.get(reverse('ingredients:ingredient_list'), {'q': 'GARLIC'})
		self.assertEqual(len(response.context['ingredients']), 1)

	def test_ingredient_list_ordered_by_name(self):
		"""Ingredients are ordered alphabetically by name."""
		response = self.client.get(reverse('ingredients:ingredient_list'))
		names = [i.name for i in response.context['ingredients']]
		self.assertEqual(names, ['Garlic', 'Olive Oil', 'Onions', 'Tomatoes'])

	def test_ingredient_list_contains_ingredient_name(self):
		"""Ingredient list page contains ingredient names."""
		response = self.client.get(reverse('ingredients:ingredient_list'))
		self.assertContains(response, 'Tomatoes')
		self.assertContains(response, 'Onions')
		self.assertContains(response, 'Garlic')

	def test_ingredient_list_shows_default_unit(self):
		"""Ingredient list page shows default units."""
		response = self.client.get(reverse('ingredients:ingredient_list'))
		self.assertContains(response, 'cloves')
