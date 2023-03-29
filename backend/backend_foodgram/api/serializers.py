import base64

from django.core.files.base import ContentFile
from django.db.utils import IntegrityError
from djoser.serializers import UserSerializer
from recipes.models import (FavoriteRecipe, Ingredient, Quantity, Recipe,
                            ShoppingCart, Tag)
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from users.models import CustomUser, Subscribe


class CustomUserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'first_name', 'last_name', 'email',
                  'password')

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = super().create(validated_data)
        user.set_password(password)
        user.save()
        return user


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            forma, imgstr = data.split(';base64,')
            ext = forma.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class SubscribeTrueOrFalseSerializer(serializers.ModelSerializer):
    '''
    Проверяет подписан или нет текущий юзер на автора. Если подписан
    возвращает True, иначе возвращает False
    '''
    author = serializers.IntegerField(source='author.pk', required=False)
    subscriber = serializers.IntegerField(source='subscriber.pk',
                                          required=False)

    class Meta:
        model = Subscribe
        fields = '__all__'

    def to_representation(self, instance):
        currentuser = self.context.get('request').user
        if currentuser.is_anonymous:
            return False
        return (instance.instance
                .subscribers.filter(subscriber=currentuser).exists())


class SpecialUserSerializer(UserSerializer):
    '''
    Возвращает данные пользователя с отметкой подписан или нет
    на этого пользователя текущий пользователь.
    '''
    is_subscribed = SubscribeTrueOrFalseSerializer(source='subscribers')

    class Meta:
        model = CustomUser
        fields = ('id', 'first_name', 'last_name', 'email', 'username',
                  'is_subscribed')


class QuantitySerializer(serializers.ModelSerializer):
    '''
    Возвращает ингредиент и его количество в рецепте.
    В ответе даёт id ингредиента.
    '''
    name = serializers.CharField(source='ingredient.name', read_only=True)
    measurement_unit = serializers.CharField(source='ingredient.measure',
                                             read_only=True)
    id = serializers.PrimaryKeyRelatedField(source='ingredient.pk',
                                            queryset=Ingredient.objects.all())

    class Meta:
        model = Quantity
        fields = ('id', 'name', 'amount', 'measurement_unit')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class FavoriteSerializer(serializers.ModelSerializer):
    '''
    Возвращает True если рецепт добавлен в избранное, иначе False.
    '''
    user = serializers.ImageField(source='user.pk', required=False)
    recipe = serializers.IntegerField(source='recipe.pk', required=False)

    class Meta:
        model = FavoriteRecipe
        fields = '__all__'

    def to_representation(self, instance):
        currentuser = self.context.get('request').user
        if currentuser.is_anonymous:
            return False
        return instance.instance.users.filter(user=currentuser).exists()


class ShoppingCartSerializer(serializers.ModelSerializer):
    '''
    Возвращает True если рецепт добавлен в список покупок, иначе False.
    '''
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    recipes = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = ShoppingCart
        fields = ('id', 'recipes', 'user')

    def to_representation(self, instance):
        currentuser = self.context.get('request').user
        if currentuser.is_anonymous:
            False
        return (instance.instance
                .shopping_carts.filter(user=currentuser).exists())


class RecipeSerializer(serializers.ModelSerializer):
    '''
    Сериализатор для SAFE запросов.
    '''
    is_in_shopping_cart = ShoppingCartSerializer(source='shopping_carts')
    is_favorited = FavoriteSerializer(source='users')
    author = SpecialUserSerializer()
    tags = TagSerializer(many=True)
    ingredients = QuantitySerializer(
        source='quantity_set',
        many=True
    )

    class Meta:
        model = Recipe
        exclude = ('pub_date',)


class RecipeCreateSerializer(serializers.ModelSerializer):
    '''
    Сериализатор для POST и PATCH запросов.
    '''
    author = serializers.PrimaryKeyRelatedField(
        default=serializers.CurrentUserDefault(),
        read_only=True
    )
    ingredients = QuantitySerializer(source='quantity_set', many=True)
    image = Base64ImageField(required=True)

    class Meta:
        model = Recipe
        exclude = ('pub_date', )

    def validate(self, attrs):
        if not attrs['quantity_set']:
            raise ValidationError('You need add any ingredients.')
        ingredients = []
        for item in attrs['quantity_set']:
            ingredient = item['ingredient']['pk']
            ingredients.append(ingredient)
            if item['amount'] <= 0:
                raise ValidationError('Количество не может быть 0 или '
                                      'отрицательным значением.')
        if len(ingredients) != len(set(ingredients)):
            raise ValidationError('Ингредиенты не должны повторяться.')
        ingredients_id_for_check = [
            ingredient.pk for ingredient in ingredients
        ]
        if not Ingredient.objects.filter(pk__in=ingredients_id_for_check):
            raise ValidationError('Проверьте, что ингредиенты '
                                  'существуют в базе')
        if len(attrs['tags']) != len(set(attrs['tags'])):
            raise ValidationError('Теги не должны повторяться')
        tags_for_check = [tag.pk for tag in attrs['tags']]
        if not Tag.objects.filter(pk__in=tags_for_check).exists():
            raise ValidationError('Проверьте, что теги существуют.')
        return super().validate(attrs)

    def create(self, validated_data):
        ingredients = validated_data.pop('quantity_set')
        tags = validated_data.pop('tags')
        validated_data['author'] = self.context.get('request').user
        recipe = Recipe.objects.create(**validated_data)
        tags = [tag.pk for tag in tags]
        recipe.tags.set(tags)
        for ingredient in ingredients:
            ingredient, amount = ingredient.items()
            ingredient = ingredient[1]['pk']
            amount = amount[1]
            obj, created = Quantity.objects.get_or_create(
                recipe=recipe, ingredient=ingredient,
                defaults={'amount': amount}
            )
            if created is not True:
                obj.amount += amount
                obj.save()
        return recipe

    def update(self, instance, validated_data):
        instance.quantity_set.all().delete()
        ingredients = validated_data.pop('quantity_set')
        tags = validated_data.pop('tags')
        Recipe.objects.filter(pk=instance.pk).update(**validated_data)
        recipe = Recipe.objects.get(pk=instance.pk)
        tags = [tag.pk for tag in tags]
        recipe.tags.set(tags)
        for ingredient in ingredients:
            ingredient, amount = ingredient.items()
            ingredient = ingredient[1]['pk']
            amount = amount[1]
            obj, created = Quantity.objects.get_or_create(
                recipe=recipe, ingredient=ingredient,
                defaults={'amount': amount}
            )
            if created is not True:
                obj.amount += amount
                obj.save()
        return recipe

    def to_representation(self, instance):
        serializer = RecipeSerializer(context=self.context)
        return serializer.to_representation(instance)


class FilterRecipesLimitSerializer(serializers.ListSerializer):
    '''
    Фильтр для вложенного сериализатора. Ограничивает количество рецептов
    автора показываемых в ответе.
    '''
    def to_representation(self, data):
        if 'recipes_limit' not in self.context.get('request').query_params:
            return super().to_representation(data)
        try:
            recipes_limit = int(
                self.context.get('request').query_params.get('recipes_limit')
            )
        except ValueError:
            raise ValidationError('recipes_limit должен быть целым числом')
        return super().to_representation(data)[:recipes_limit]


class RecipeSubscriptionsSerializer(serializers.ModelSerializer):
    '''
    Вложенный сериализатор. Возвращает рецепты автора.
    '''
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        list_serializer_class = FilterRecipesLimitSerializer


class SubscriptionsSerializer(SpecialUserSerializer):
    '''
    Возвращает авторов на которых подписан текущий пользователь.
    '''
    recipes = RecipeSubscriptionsSerializer(read_only=True, many=True)
    recipes_count = serializers.IntegerField()

    class Meta:
        model = CustomUser
        fields = ('id', 'first_name', 'last_name', 'email', 'username',
                  'recipes', 'recipes_count')


class SubscribeSerializer(serializers.ModelSerializer):
    '''
    Создаёт подписку на автора. Валидирует повторную подписку и подписку
    на самого себя.
    '''
    class Meta:
        model = Subscribe
        fields = '__all__'

    def create(self, validated_data):
        try:
            inst = super().create(validated_data)
        except IntegrityError:
            raise ValidationError(
                'Вы уже подписаны на этого автора или '
                'подписываетесь сами на себя'
            )
        return inst


class SimpleRecipeSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(read_only=True)
    name = serializers.CharField(read_only=True)
    image = Base64ImageField(read_only=True)
    cooking_time = serializers.IntegerField(read_only=True)

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class AnonimusRecipeSerializer(serializers.ModelSerializer):
    # author = serializers.PrimaryKeyRelatedField(read_only=True)
    author = UserSerializer(read_only=True)
    id = serializers.PrimaryKeyRelatedField(read_only=True)
    name = serializers.CharField(read_only=True)
    image = Base64ImageField(read_only=True)
    cooking_time = serializers.IntegerField(read_only=True)
    tags = TagSerializer(many=True)
    ingredients = QuantitySerializer(
        source='quantity_set',
        many=True
    )

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time', 'author', 'text',
                  'tags', 'ingredients')


class ShoppingCartPostDeleteSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        read_only=True, default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = ShoppingCart
        fields = ('id', 'recipes', 'user')

    def update(self, instance, validated_data):
        if self.context.get('request').method == 'DELETE':
            set_recipe = [
                recipe.pk for recipe in validated_data.get('recipes')
            ]
            instance.recipes.set(set_recipe)
            return instance
        add_recipe = validated_data.get('recipes')[0].pk
        instance.recipes.add(add_recipe)
        return instance


class FavoritePostDeleteSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.all(),
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = FavoriteRecipe
        fields = ('id', 'recipe', 'user')

    def create(self, validated_data):
        try:
            inst = super().create(validated_data)
        except IntegrityError:
            raise ValidationError('Этот рецепт уже добавлен в избранное')
        return inst
