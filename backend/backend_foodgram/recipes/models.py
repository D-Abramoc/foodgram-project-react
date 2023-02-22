from django.db import models
from django.conf import settings
from users.models import CustomUser

from backend_foodgram import settings


class Ingredient(models.Model):
    name = models.CharField(max_length=settings.MAX_LENGTH_NAME,
                            verbose_name='Название')
    # quantity = models.FloatField(verbose_name='Количество')
    measure = models.CharField(max_length=settings.MAX_LENGTH_NAME,
                               verbose_name='Единицы измерения')

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=settings.MAX_LENGTH_NAME,
                            verbose_name='Тег')
    hex_color = models.CharField(max_length=settings.MAX_LENGTH_HEX_COLOR,
                                 verbose_name='Цвет')
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
    image = models.ImageField(verbose_name='Фото готового блюда', unique=True,
                              upload_to='recipes/')
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

    def __str__(self) -> str:
        return self.title


class Quantity(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity = models.FloatField(verbose_name='Количество')
