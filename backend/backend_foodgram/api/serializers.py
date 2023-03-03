import re

from rest_framework import serializers
from djoser.serializers import UserCreateSerializer, UserSerializer
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from recipes.models import Ingredient, Recipe, Tag
from users.models import CustomUser, Subscribe


class SubscribeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscribe
        fields = '__all__'


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


class CreateUserSerializer(UserCreateSerializer):

    def validate(self, attrs):
        user = CustomUser(**attrs)
        password = attrs.get("password")

        try:
            validate_password(password, user)
        except ValidationError as e:
            serializer_error = serializers.as_serializer_error(e)
            raise serializers.ValidationError(
                {"password": serializer_error["non_field_errors"]}
            )

        return attrs


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'email', 'first_name', 'last_name')


class CustomUserPOSTSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = (
            'id', 'username', 'email', 'first_name', 'last_name', 'password'
        )

    def validate_username(self, value):
        name = value.lower()
        if name == 'me':
            raise serializers.ValidationError(
                'Невозможно создать пользователя с именем me'
            )
        elif re.fullmatch(r'^[\w.@+-]+\Z', value):
            return value
        raise serializers.ValidationError(
            'Невозможно создать пользователя с таким набором симвлолов'
        )


class ChangePasswordSerializer(serializers.ModelSerializer):
    new_password = serializers.CharField(required=True)
    current_password = serializers.CharField(required=True)

    class Meta:
        model = CustomUser
        fields = ('new_password', 'current_password')

    def validate_current_password(self, value):
        if not self.instance.check_password(value):
            raise serializers.ValidationError('Wrong password!')
        return value


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
        # fields = '__all__'
        exclude = ('pub_date',)

    # def validate(self, attrs):
    #     if 'ingredients' not in self.initial_data:
    #         raise serializers.ValidationError(
    #             'You need to add the ingredients'
    #         )
    #     if attrs.get('ingedients'):
    #         raise serializers.ValidationError(
    #             'You need to add the ingredients'
    #         )
    #     return super().validate(attrs)

    # def validate_ingredients(self, value):
    #     if not value:
    #         raise serializers.ValidationError(
    #             'You need to add the ingredients'
    #         )
    #     return value
