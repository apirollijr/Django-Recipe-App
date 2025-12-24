from django.db import models
from django.conf import settings


class Recipe(models.Model):
	title = models.CharField(max_length=200)
	description = models.TextField(blank=True)
	instructions = models.TextField()
	author = models.ForeignKey(
		settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
	)
	category = models.ForeignKey(
		'categories.Category', on_delete=models.SET_NULL, null=True, blank=True, related_name='recipes'
	)
	prep_time_minutes = models.PositiveIntegerField(default=0)
	cook_time_minutes = models.PositiveIntegerField(default=0)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self) -> str:
		return self.title


class RecipeIngredient(models.Model):
	recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='recipe_ingredients')
	ingredient = models.ForeignKey('ingredients.Ingredient', on_delete=models.CASCADE, related_name='ingredient_recipes')
	quantity = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
	unit = models.CharField(max_length=32, blank=True)
	notes = models.CharField(max_length=255, blank=True)

	class Meta:
		unique_together = ('recipe', 'ingredient')

	def __str__(self) -> str:
		base = f"{self.ingredient.name}"
		if self.quantity:
			base = f"{self.quantity} {self.unit} {base}".strip()
		return base
