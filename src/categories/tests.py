from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from recipes.models import Recipe
from .models import Category


User = get_user_model()


class CategoryModelTests(TestCase):
	def test_str(self):
		cat = Category.objects.create(name="Desserts", slug="desserts")
		self.assertEqual(str(cat), "Desserts")


class CategoryListViewTests(TestCase):
	@classmethod
	def setUpTestData(cls):
		cls.user = User.objects.create_user(username="chef", password="pass12345")
		
		cls.category1 = Category.objects.create(name="Italian", slug="italian")
		cls.category2 = Category.objects.create(name="Mexican", slug="mexican")
		cls.category3 = Category.objects.create(name="Indian", slug="indian")
		
		# Add recipes to categories for count testing
		Recipe.objects.create(
			title="Pasta",
			instructions="Cook it",
			category=cls.category1,
		)
		Recipe.objects.create(
			title="Pizza",
			instructions="Bake it",
			category=cls.category1,
		)
		Recipe.objects.create(
			title="Tacos",
			instructions="Assemble it",
			category=cls.category2,
		)

	def test_category_list_status_code(self):
		"""Category list page returns 200."""
		response = self.client.get(reverse('categories:category_list'))
		self.assertEqual(response.status_code, 200)

	def test_category_list_template(self):
		"""Category list uses correct template."""
		response = self.client.get(reverse('categories:category_list'))
		self.assertTemplateUsed(response, 'categories/category_list.html')

	def test_category_list_contains_all_categories(self):
		"""Category list contains all categories."""
		response = self.client.get(reverse('categories:category_list'))
		self.assertEqual(len(response.context['categories']), 3)

	def test_category_list_has_recipe_counts(self):
		"""Categories have correct recipe counts."""
		response = self.client.get(reverse('categories:category_list'))
		categories = {c.name: c for c in response.context['categories']}
		self.assertEqual(categories['Italian'].recipe_count, 2)
		self.assertEqual(categories['Mexican'].recipe_count, 1)
		self.assertEqual(categories['Indian'].recipe_count, 0)

	def test_category_list_search_filter(self):
		"""Search filter returns matching categories."""
		response = self.client.get(reverse('categories:category_list'), {'q': 'Italian'})
		self.assertEqual(len(response.context['categories']), 1)
		self.assertEqual(response.context['categories'][0].name, 'Italian')
		self.assertEqual(response.context['search_query'], 'Italian')

	def test_category_list_search_partial_match(self):
		"""Search filter works with partial matches."""
		response = self.client.get(reverse('categories:category_list'), {'q': 'ian'})
		# Matches Italian and Indian
		self.assertEqual(len(response.context['categories']), 2)

	def test_category_list_search_no_results(self):
		"""Search with no matches returns empty list."""
		response = self.client.get(reverse('categories:category_list'), {'q': 'French'})
		self.assertEqual(len(response.context['categories']), 0)

	def test_category_list_search_case_insensitive(self):
		"""Search is case insensitive."""
		response = self.client.get(reverse('categories:category_list'), {'q': 'ITALIAN'})
		self.assertEqual(len(response.context['categories']), 1)

	def test_category_list_ordered_by_name(self):
		"""Categories are ordered alphabetically by name."""
		response = self.client.get(reverse('categories:category_list'))
		names = [c.name for c in response.context['categories']]
		self.assertEqual(names, ['Indian', 'Italian', 'Mexican'])

	def test_category_list_contains_category_name(self):
		"""Category list page contains category names."""
		response = self.client.get(reverse('categories:category_list'))
		self.assertContains(response, 'Italian')
		self.assertContains(response, 'Mexican')
		self.assertContains(response, 'Indian')
