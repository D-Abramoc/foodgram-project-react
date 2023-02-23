from django.contrib import admin
from .models import Tag, Ingredient, Recipe, Quantity


class QuantityInLine(admin.TabularInline):
    model = Quantity
    extra = 1


class RecipeAdmin(admin.ModelAdmin):
    inlines = (QuantityInLine,)


admin.site.register(Ingredient)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag)
