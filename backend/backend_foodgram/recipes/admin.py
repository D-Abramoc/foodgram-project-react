from django.contrib import admin
from .models import (Tag, Ingredient, Recipe, Quantity, ShoppingCart,
                     FavoriteRecipe)


class QuantityInLine(admin.TabularInline):
    model = Quantity
    extra = 1


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


admin.site.register(Tag)
admin.site.register(ShoppingCart)
admin.site.register(FavoriteRecipe)
admin.site.register(Quantity)
