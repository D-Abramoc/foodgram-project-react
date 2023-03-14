from http import HTTPStatus

from django.test import TestCase
import json
from recipes.models import (Tag, Recipe, Ingredient,
                            ShoppingCart, FavoriteRecipe, Quantity)
from users.models import CustomUser, Subscribe


class APITest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = CustomUser.objects.create(
            first_name='First',
            last_name='Last_1',
            username='first_last',
            email='f@fake.fake'
        )
        cls.tag = Tag.objects.create(
            name='test_tag_1',
            color='#000000',
            slug='slug1'
        )
        cls.ingredient = Ingredient.objects.create(
            name='kakaxa',
            measure='kg'
        )
        cls.recipe = Recipe.objects.create(
            author=cls.user,
            name='Recipe 1',
            text='Text',
            cooking_time=5
        )
        cls.quantity = Quantity.objects.create(
            recipe=cls.recipe,
            ingredient=cls.ingredient,
            amount=100
        )
        cls.recipe.ingredients.set(
            Ingredient.objects.filter(pk=cls.ingredient.pk)
        )
        cls.recipe.tags.set(Tag.objects.filter(pk=cls.tag.pk))

    def test_anon_get(self):
        """
        Доступность страниц для анонимного пользователя
        """
        addresses = (
            ('/api/recipes/', HTTPStatus.OK),
            (f'/api/recipes/{self.recipe.pk}/', HTTPStatus.OK),
            (f'/api/users/{self.user.pk}/', HTTPStatus.OK),
            ('/api/users/', HTTPStatus.UNAUTHORIZED),
            ('/api/users/me/', HTTPStatus.UNAUTHORIZED),
            ('/api/tags/', HTTPStatus.OK),
            (f'/api/tags/{self.tag.pk}/', HTTPStatus.OK),
            ('/api/users/subscriptions/', HTTPStatus.UNAUTHORIZED),
            ('/api/ingredients/', HTTPStatus.OK),
            (f'/api/ingredients/{self.ingredient.pk}/', HTTPStatus.OK)
        )
        for address, expected_code in addresses:
            with self.subTest(address=address):
                response = self.client.get(address)
                self.assertEqual(
                    response.status_code, expected_code,
                    (f'Address {address} '
                     f'return status {response.status_code}')
                )

    def test_registration_user(self):
        """
        Регистрация пользователя и получение токена
        """
        number_of_users = CustomUser.objects.count()
        data = {
            'first_name': 'Jack',
            'last_name': 'Sparrow',
            'username': 'pirat',
            'email': 'pirat@fake.fake',
            'password': 'pass__word'
        }
        self.client.post(
            '/api/users/', data=data
        )
        self.assertEqual(CustomUser.objects.count(), number_of_users + 1)
        data = {
            'email': 'pirat@fake.fake',
            'password': 'pass__word'
        }
        response = self.client.post(
            '/api/auth/token/login/', data=data
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
