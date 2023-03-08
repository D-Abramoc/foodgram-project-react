from rest_framework import serializers
from djoser.serializers import UserSerializer
from django.shortcuts import get_object_or_404

from recipes.models import (Ingredient, Recipe, ShoppingCart, Tag,
                            FavoriteRecipe, Quantity)
from users.models import CustomUser, Subscribe


class SpecialUserSerializer(UserSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'first_name', 'last_name', 'email', 'username',)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        user = self.context.get('request').user
        subscribers = [
            subscriber.subscriber for subscriber in user.subscribers.all()
        ]
        if instance in subscribers:
            representation['is_subscribed'] = True
            return representation
        representation['is_subscribed'] = False
        return representation


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


class RecipeSerializer(serializers.ModelSerializer):
    author = SpecialUserSerializer()
    tags = TagSerializer(many=True)
    # ingredients = IngredientSerializer(many=True)
    ingredients = QuantitySerializer(
        source='quantity_set',
        many=True
    )

    class Meta:
        model = Recipe
        exclude = ('pub_date',)

    # def create(self, validated_data):
    #     ingredients = validated_data.pop('quantity_set')
    #     tags = validated_data.pop('tags')
    #     recipe = Recipe.objects.create(**validated_data)
    #     tags = [tag.pk for tag in tags]
    #     recipe.tags.set(tags)
    #     # ingredients['recipe'] = recipe
    #     ingredient = ingredients[0]['id']
    #     ingredient = get_object_or_404(Ingredient, pk=ingredient)
    #     amount = ingredients[0]['amount']
    #     item_of_quantity = Quantity(recipe=recipe,
    #                                 ingredient=ingredient,
    #                                 amount=amount)
    #     item_of_quantity.save()
    #     return recipe


class NonModelSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    amount = serializers.FloatField()


class RecipeCreateSerializer(serializers.ModelSerializer):
    ingredients = QuantitySerializer(source='quantity_set', many=True)

    class Meta:
        model = Recipe
        exclude = ('pub_date', )

    def create(self, validated_data):
        ingredients = validated_data.pop('quantity_set')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        tags = [tag.pk for tag in tags]
        recipe.tags.set(tags)
        # ingredients['recipe'] = recipe
        ingredient = ingredients[0]['ingredient']['pk']
        # ingredient = get_object_or_404(Ingredient, pk=ingredient)
        amount = ingredients[0]['amount']
        item_of_quantity = Quantity(recipe=recipe,
                                    ingredient=ingredient,
                                    amount=amount)
        item_of_quantity.save()
        return recipe
    
    # def to_representation(self, instance):
    #     serializer = RecipeCreateSerializer()
    #     representation = super().to_representation(instance)
    #     return representation


class RecipeSubscriptionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionsSerializer(SpecialUserSerializer):
    recipes = RecipeSubscriptionsSerializer(read_only=True, many=True)
    recipes_count = serializers.IntegerField()

    class Meta:
        model = CustomUser
        fields = ('id', 'first_name', 'last_name', 'email', 'username',
                  'recipes', 'recipes_count')


class SubscribeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Subscribe
        fields = ('id', 'author', 'subscriber')


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = FavoriteRecipe
        fields = '__all__'


class ShoppingCartSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShoppingCart
        fields = ('id', 'recipes', 'user')
        read_only_fields = ('user',)


class ShoppingCartDeleteRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingCart
        fields = '__all__'
        read_only_fields = ('user', )
