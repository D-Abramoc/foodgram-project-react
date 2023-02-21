from django.contrib import admin
from .models import Tag, Ingredient, Recipe


admin.site.register(Ingredient)
admin.site.register(Recipe)
admin.site.register(Tag)
