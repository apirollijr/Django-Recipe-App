from django.contrib import admin
from .models import Recipe, RecipeIngredient


class RecipeIngredientInline(admin.TabularInline):
	model = RecipeIngredient
	extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
	list_display = ("title", "category", "author", "created_at")
	search_fields = ("title", "description")
	list_filter = ("category",)
	inlines = [RecipeIngredientInline]


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
	list_display = ("recipe", "ingredient", "quantity", "unit")
