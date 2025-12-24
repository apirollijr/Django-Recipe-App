from django.test import TestCase
from .models import Category


class CategoryModelTests(TestCase):
	def test_str(self):
		cat = Category.objects.create(name="Desserts", slug="desserts")
		self.assertEqual(str(cat), "Desserts")
