from django.urls import path
from .views import list_main_categories, list_subcategories

urlpatterns = [
    path('main-categories/', list_main_categories, name='list_main_categories'),
    path('subcategories/<int:main_category_id>/', list_subcategories, name='list_subcategories'),
]
