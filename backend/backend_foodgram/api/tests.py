from http import HTTPStatus

from django.test import TestCase, Client
import json
from recipes.models import (Tag, Recipe, Ingredient,
                            ShoppingCart, FavoriteRecipe, Quantity)
from users.models import CustomUser, Subscribe
from rest_framework.test import APIRequestFactory, APITestCase, APIClient


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
        # bulk_users = []
        # fields = ('first_name', 'last_name', 'username', 'email', 'password')
        # for i in range(1, 30):
        #     data = (f'Name{i}', f'Surname{i}', f'username{i}',
        #             f'mail{i}@fake.fake', 'pass__word{i}')
        #     data_for_create = dict(zip(fields, data))
        #     user = CustomUser.objects.create(**data_for_create)
        #     bulk_users.append(user)
        # CustomUser.objects.bulk_create(bulk_users)
        cls.tag = Tag.objects.create(
            name='test_tag_1',
            color='#000000',
            slug='slug1'
        )
        # bulk_tag = []
        # fields = ('name', 'color', 'slug')
        # for i in range(1, 4):
        #     data = (f'tag{i}', f'#00000{i}', f'slug_{i}')
        #     data_for_create = dict(zip(fields, data))
        #     tag = Tag(**data_for_create)
        #     bulk_tag.append(tag)
        # Tag.objects.bulk_create(bulk_tag)
        cls.ingredient = Ingredient.objects.create(
            name='kakaxa',
            measure='kg'
        )
        # bulk_ingredient = []
        # fields = ('name', 'measure')
        # for i in range(1, 61):
        #     data = (f'ingredient{i}', 'kg')
        #     data_for_create = dict(zip(fields, data))
        #     ingredient = Ingredient(**data_for_create)
        #     bulk_ingredient.append(ingredient)
        # Ingredient.objects.bulk_create(bulk_ingredient)
        cls.recipe = Recipe.objects.create(
            author=cls.user,
            name='Recipe 1',
            text='Text',
            cooking_time=5
        )
        # bulc_recipe = []
        # fields = ('author', 'name', 'text', 'cooking_time')
        # for i in range(2, 20):
        #     data = (CustomUser.objects.get(pk=i), f'Recipe{i}', 'Text{i}', i)
        #     data_for_create = dict(zip(fields, data))
        #     recipe = Recipe(**data_for_create)
        #     bulc_recipe.append(recipe)
        # Recipe.objects.bulk_create(bulc_recipe)
        # for i in Recipe.objects.all():
        #     Quantity.objects.create(
        #         recipe=i,
        #         ingredient=Ingredient.objects.get(pk=i.pk),
        #         amount=100
        #     )
        #     Quantity.objects.create(
        #         recipe=i,
        #         ingredient=Ingredient.objects.get(pk=i.pk + 1),
        #         amount=150
        #     )
        #     ingredients = (Ingredient.objects.get(pk=i.pk).pk,
        #                    Ingredient.objects.get(pk=i.pk+1).pk)
        #     i.ingredients.set(ingredients)
        #     i.tags.set(Tag.objects.filter(pk=cls.tag.pk))

    def setUp(self):
        self.auth_client = Client()
        self.auth_client.force_login(self.user)

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
        Регистрация пользователя, получение токена
        """
        number_of_users = CustomUser.objects.count()
        data = {
            'first_name': 'Jack',
            'last_name': 'Sparrow',
            'username': 'pirat',
            'email': 'pirat@fake.fake',
            'password': 'pass__word'
        }
        # Registration of new user
        self.client.post(
            '/api/users/', data=data
        )
        self.assertEqual(CustomUser.objects.count(), number_of_users + 1)
        data = {
            'email': 'pirat@fake.fake',
            'password': 'pass__word'
        }
        # login
        response = self.client.post(
            '/api/auth/token/login/', data=data
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_logout(self):
        response = self.auth_client.post(
            '/api/auth/token/logout'
        )
        self.assertEqual(response.status_code, HTTPStatus.NO_CONTENT)

    def test_list_of_users(self):
        """
        GET to api/users/ from aut_client
        """
        expected_keys = ('count', 'next', 'previous', 'results')
        response = self.auth_client.get('/api/users/')
        response_dict = json.loads(response._container[0])
        self.assertEqual(tuple(response_dict.keys()), expected_keys)


class AuthUserTest(TestCase):

    def test_users(self):
        bulk_users = []
        fields = ('first_name', 'last_name', 'username', 'email', 'password')
        for i in range(1, 30):
            data = (f'Name{i}', f'Surname{i}', f'username{i}',
                    f'mail{i}@fake.fake', 'pass__word{i}')
            data_for_create = dict(zip(fields, data))
            user = CustomUser(**data_for_create)
            bulk_users.append(user)
        CustomUser.objects.bulk_create(bulk_users)
        auth_user = Client()
        auth_user.force_login(CustomUser.objects.first())
        response = auth_user.get('/api/users/')
        print(response)


class API_Test(APITestCase):

    def test_get(self):
        user = CustomUser.objects.create(username='Ad')
        bulk_users = []
        fields = ('first_name', 'last_name', 'username', 'email', 'password')
        for i in range(1, 30):
            data = (f'Name{i}', f'Surname{i}', f'username{i}',
                    f'mail{i}@fake.fake', 'pass__word{i}')
            data_for_create = dict(zip(fields, data))
            user_to_list = CustomUser(**data_for_create)
            bulk_users.append(user_to_list)
        CustomUser.objects.bulk_create(bulk_users)
        auth_client = APIClient()
        auth_client.force_authenticate(user)
        response = auth_client.get('/api/users/')
        factory = APIRequestFactory()
        request = factory.get('/api/users/')
        print(request)
