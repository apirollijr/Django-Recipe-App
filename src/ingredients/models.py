from django.db import models


class Ingredient(models.Model):
	name = models.CharField(max_length=120, unique=True)
	default_unit = models.CharField(max_length=20, blank=True)

	def __str__(self) -> str:
		return self.name
