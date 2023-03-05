from rest_framework import serializers
from djoser.serializers import UserSerializer

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


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class RecipeSerializer(serializers.ModelSerializer):
    author = SpecialUserSerializer()
    tags = TagSerializer(many=True)
    ingredients = IngredientSerializer(many=True)

    class Meta:
        model = Recipe
        exclude = ('pub_date',)


class QuantitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Quantity
        fields = ('quantity',)


class IngredientAmountSerializer(serializers.ModelSerializer):
    amount = serializers.FloatField()
    id = serializers.PrimaryKeyRelatedField(
        # read_only=True,
        queryset=Ingredient.objects.all()
    )

    class Meta:
        model = Ingredient
        fields = ('id','amount')


class RecipeCreateSerializer(serializers.ModelSerializer):
    ingredients = IngredientAmountSerializer(many=True)

    class Meta:
        model = Recipe
        exclude = ('pub_date', )
    
    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        tags = [tag.pk for tag in tags]
        recipe.tags.set(tags)
        # ingredients['recipe'] = recipe
        Quantity.objects.create(recipe=recipe, **ingredients[0])
        return recipe


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
