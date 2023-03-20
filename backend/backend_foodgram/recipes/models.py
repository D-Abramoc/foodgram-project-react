from django.db import models
from django.conf import settings
from users.models import CustomUser

from .validators import validate_minimum, validate_string


class Ingredient(models.Model):
    name = models.CharField(max_length=settings.MAX_LENGTH_NAME,
                            verbose_name='Название')
    measure = models.CharField(max_length=settings.MAX_LENGTH_NAME,
                               verbose_name='Единицы измерения')

    class Meta:
        ordering = ('name',)
        verbose_name = 'ингредиент'
        verbose_name_plural = 'ингредиенты'

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=settings.MAX_LENGTH_NAME,
                            verbose_name='Тег', unique=True)
    color = models.CharField(max_length=settings.MAX_LENGTH_HEX_COLOR,
                             verbose_name='Цвет', unique=True)
    slug = models.SlugField(unique=True, verbose_name='SLUG',
                            max_length=settings.MAX_LENGTH_NAME)

    class Meta:
        verbose_name = 'тег'
        verbose_name_plural = 'теги'

    def __str__(self) -> str:
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE,
                               verbose_name='Автор', related_name='recipes')
    name = models.CharField(max_length=settings.MAX_LENGTH_NAME,
                            unique=True, verbose_name='Название блюда',
                            validators=(validate_string, ))
    image = models.ImageField(verbose_name='Фото готового блюда', unique=False,
                              upload_to='recipes/images/')
    text = models.TextField(verbose_name='Описание приготовления блюда',
                            help_text='Опишите порядок приготовления блюда',
                            validators=(validate_string,))
    ingredients = models.ManyToManyField(Ingredient, through='Quantity',
                                         related_name='recipes')
    tags = models.ManyToManyField(Tag, related_name='recipes')
    cooking_time = models.IntegerField(
        verbose_name='Время приготовления в минутах',
        validators=(validate_minimum, )
    )
    pub_date = models.DateTimeField(verbose_name='Дата добавления рецепта',
                                    auto_now_add=True)

    class Meta:
        verbose_name = 'рецепт'
        verbose_name_plural = 'рецепты'
        ordering = ('-pub_date',)

    def __str__(self) -> str:
        return self.name


class Quantity(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE,
                                   verbose_name='Ингредиент')
    amount = models.PositiveIntegerField(verbose_name='Количество',
                                         blank=False,
                                         null=False,
                                         validators=(validate_minimum,))

    class Meta:
        verbose_name = 'запись о количестве ингредиента в рецепте'
        verbose_name_plural = 'количество ингредиентов'

    def __str__(self):
        return (f'Рецепт {self.recipe.name} '
                f'содержит {self.amount} {self.ingredient.measure} '
                f'ингредиента {self.ingredient.name}')


class ShoppingCart(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    recipes = models.ManyToManyField(Recipe, related_name='shopping_carts')

    class Meta:
        verbose_name = 'список покупок'
        verbose_name_plural = 'список покупок'

    def __str__(self):
        return (f'Список покупок юзера {self.user.username}')


class FavoriteRecipe(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE,
                             related_name='favorite_recipes')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               related_name='users')

    class Meta:
        verbose_name = 'избранные рецепты'
        verbose_name_plural = 'избранные рецепты'
