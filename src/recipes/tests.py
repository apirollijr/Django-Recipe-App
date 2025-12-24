from django.test import TestCase
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
