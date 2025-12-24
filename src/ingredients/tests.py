from django.test import TestCase
from .models import Ingredient


class IngredientModelTests(TestCase):
	def test_str(self):
		ing = Ingredient.objects.create(name="Sugar", default_unit="g")
		self.assertEqual(str(ing), "Sugar")
