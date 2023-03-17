import base64

from django.core.files.base import ContentFile
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from djoser.serializers import UserSerializer

from recipes.models import (Ingredient, Recipe, ShoppingCart, Tag,
                            FavoriteRecipe, Quantity)
from users.models import CustomUser, Subscribe


class MeSerializer(serializers.ListSerializer):
    def to_representation(self, data):
        return super().to_representation(data)


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


class SubscribeSerializer(serializers.ModelSerializer):
    author = serializers.IntegerField(source='author.pk', required=False)
    subscriber = serializers.IntegerField(source='subscriber.pk',
                                          required=False)

    class Meta:
        model = Subscribe
        fields = '__all__'

    def to_representation(self, instance):
        currentuser = self.context.get('request').user
        if instance.instance.subscribers.filter(subscriber=currentuser):
            return True
        return False


class SpecialUserSerializer(UserSerializer):
    is_subscribed = SubscribeSerializer(source='subscribers')

    class Meta:
        model = CustomUser
        fields = ('id', 'first_name', 'last_name', 'email', 'username',
                  'is_subscribed')
    
    def to_representation(self, instance):  # remove while refactoring
        repres = super().to_representation(instance)
        return repres


class UserSerializerForRecipeCreateSerializer(UserSerializer):
    is_subscribed = SubscribeSerializer(source='subscribers')

    class Meta:
        model = CustomUser
        fields = ('id', 'first_name', 'last_name', 'email', 'username',
                  'is_subscribed')


class QuantitySerializer(serializers.ModelSerializer):
    ingredient = serializers.CharField(source='ingredient.name',
                                       read_only=True)
    mesurement_unit = serializers.CharField(source='ingredient.measure',
                                            read_only=True)
    id = serializers.PrimaryKeyRelatedField(source='ingredient.pk',
                                            queryset=Ingredient.objects.all())

    class Meta:
        model = Quantity
        fields = ('id', 'ingredient', 'amount', 'mesurement_unit')


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measure')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class FavoriteSerializer(serializers.ModelSerializer):
    user = serializers.ImageField(source='user.pk', required=False)
    recipe = serializers.IntegerField(source='recipe.pk', required=False)

    class Meta:
        model = FavoriteRecipe
        fields = '__all__'

    def to_representation(self, instance):
        currentuser = self.context.get('request').user
        if instance.instance.users.filter(user=currentuser):
            return True
        return False


class ShoppingCartSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    recipes = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = ShoppingCart
        fields = ('id', 'recipes', 'user')
        read_only_fields = ('user',)

    def to_representation(self, instance):
        currentuser = self.context.get('request').user
        if instance.instance.shopping_carts.filter(user=currentuser):
            return True
        return False


class RecipeSerializer(serializers.ModelSerializer):
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
            raise ValidationError('You need add any ingredients')
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
            item_of_quantity = Quantity(recipe=recipe,
                                        ingredient=ingredient,
                                        amount=amount)
            item_of_quantity.save()
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
            item_of_quantity = Quantity(recipe=recipe,
                                        ingredient=ingredient,
                                        amount=amount)
            item_of_quantity.save()
        return recipe

    def to_representation(self, instance):
        serializer = RecipeSerializer(context=self.context)
        representation = serializer.to_representation(instance)
        # representation.pop('is_favorited')
        # representation.pop('is_in_shopping_cart')
        return representation
    

class FilterRecipesLimitSerializer(serializers.ListSerializer):
    def to_representation(self, data):
        if 'recipes_limit' not in self.context.get('request').query_params:
            return super().to_representation(data)
        recipes_limit = int(
            self.context.get('request').query_params.get('recipes_limit')
        )
        representation = super().to_representation(data)[:recipes_limit]
        return representation


class RecipeSubscriptionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        list_serializer_class = FilterRecipesLimitSerializer


class SubscriptionsSerializer(SpecialUserSerializer):
    recipes = RecipeSubscriptionsSerializer(read_only=True, many=True)
    recipes_count = serializers.IntegerField()

    class Meta:
        model = CustomUser
        fields = ('id', 'first_name', 'last_name', 'email', 'username',
                  'recipes', 'recipes_count')

    def to_representation(self, instance):  # remove
        representation = super().to_representation(instance)
        return representation


class SubscribeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Subscribe
        fields = ('id', 'author', 'subscriber')


class SimpleRecipeSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(read_only=True)
    name = serializers.CharField(read_only=True)
    image = Base64ImageField(read_only=True)
    cooking_time = serializers.IntegerField(read_only=True)

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')

    def to_representation(self, instance):  # Удалить при рефакторинге
        repres = super().to_representation(instance)
        return repres


class AnonimusRecipeSerializer(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(read_only=True)
    id = serializers.PrimaryKeyRelatedField(read_only=True)
    name = serializers.CharField(read_only=True)
    image = Base64ImageField(read_only=True)
    cooking_time = serializers.IntegerField(read_only=True)

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time', 'author', 'text')


class ShoppingCartPostDeleteSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        read_only=True, default=serializers.CurrentUserDefault()
    )
    # recipes = serializers.PrimaryKeyRelatedField(read_only=True)

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

    def create(self, validated_data):  # remove
        return super().create(validated_data)

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

    # def to_representation(self, instance):
    #     serializer = SimpleRecipeSerializer(many=True)
    #     representation = serializer.to_representation(instance.recipes.all())
    #     return representation
