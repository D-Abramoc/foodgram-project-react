from django.db import models
from django.conf import settings
from users.models import CustomUser


class Ingredient(models.Model):
    name = models.CharField(max_length=settings.MAX_LENGTH_NAME,
                            verbose_name='Название')
    measure = models.CharField(max_length=settings.MAX_LENGTH_NAME,
                               verbose_name='Единицы измерения')

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

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
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self) -> str:
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE,
                               verbose_name='Автор', related_name='recipes')
    name = models.CharField(max_length=settings.MAX_LENGTH_NAME,
                            unique=True, verbose_name='Название блюда')
    image = models.ImageField(verbose_name='Фото готового блюда', unique=False,
                              upload_to='recipes/', blank=True)
    text = models.TextField(verbose_name='Описание приготовления блюда',
                            help_text='Опишите порядок приготовления блюда')
    ingredients = models.ManyToManyField(Ingredient, through='Quantity',
                                         related_name='recipes')
    tags = models.ManyToManyField(Tag, related_name='recipes')
    cooking_time = models.IntegerField(
        verbose_name='Время приготовления в минутах',
    )
    pub_date = models.DateTimeField(verbose_name='Дата добавления рецепта',
                                    auto_now_add=True)

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)

    def __str__(self) -> str:
        return self.name


class Quantity(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity = models.FloatField(verbose_name='Количество', blank=False,
                                 null=False)


class ShoppingCart(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    recipes = models.ManyToManyField(Recipe, related_name='shopping_carts')


class FavoriteRecipe(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE,
                             related_name='favorite_recipes')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               related_name='users')
