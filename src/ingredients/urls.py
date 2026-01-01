from django.urls import path
from . import views

app_name = 'ingredients'

urlpatterns = [
    path('', views.ingredient_list, name='ingredient_list'),
]
