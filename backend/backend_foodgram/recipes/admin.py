from django.contrib import admin
from django.db.models import Sum

from .forms import RequiredInlineFormSet
from .models import (FavoriteRecipe, Ingredient, Quantity, Recipe,
                     ShoppingCart, Tag)


class QuantityInLine(admin.TabularInline):
    model = Quantity
    extra = 1
    formset = RequiredInlineFormSet


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('author', 'name')
    list_filter = ('author', 'name', 'tags')
    inlines = (QuantityInLine,)
    fieldsets = (
        (None, {
            "fields": (
                'name', 'author', 'image', 'text', 'tags', 'cooking_time',
                'favorite_count'
            ),
        }),
    )
    readonly_fields = ('favorite_count',)

    def favorite_count(self, obj):
        return obj.users.count()

    favorite_count.short_description = 'Количество добавлений в избранное'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measure')
    list_filter = ('name',)


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            "fields": (
                'user', 'recipes', 'shopping_cart'
            ),
        }),
    )
    readonly_fields = ('shopping_cart',)

    def shopping_cart(self, obj):
        result = (Ingredient.objects.values('name')
                  .filter(recipes__in=obj.user.shoppingcart.recipes.all())
                  .annotate(ingredient_sum=Sum('quantity__amount')))
        list_of_ingredients = ''
        for item in result:
            key, value = item.values()
            row = f'{key}: {value}\n'
            list_of_ingredients += row
        return list_of_ingredients


admin.site.register(Tag)
admin.site.register(FavoriteRecipe)
admin.site.register(Quantity)
