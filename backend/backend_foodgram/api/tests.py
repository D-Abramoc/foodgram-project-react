from http import HTTPStatus

from django.test import TestCase, Client
import json
from recipes.models import (Tag, Recipe, Ingredient, Quantity)
from users.models import CustomUser
from rest_framework.test import APITestCase, APIClient


class APITest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        bulk_users = []
        fields = ('first_name', 'last_name', 'username', 'email', 'password')
        for i in range(1, 30):
            data = (f'Name{i}', f'Surname{i}', f'username{i}',
                    f'mail{i}@fake.fake', 'pass__word{i}')
            data_for_create = dict(zip(fields, data))
            user = CustomUser(**data_for_create)
            bulk_users.append(user)
        CustomUser.objects.bulk_create(bulk_users)
        cls.tag = Tag.objects.create(
            name='test_tag_1',
            color='#000000',
            slug='slug1'
        )
        bulk_tag = []
        fields = ('name', 'color', 'slug')
        for i in range(1, 4):
            data = (f'tag{i}', f'#00000{i}', f'slug_{i}')
            data_for_create = dict(zip(fields, data))
            tag = Tag(**data_for_create)
            bulk_tag.append(tag)
        Tag.objects.bulk_create(bulk_tag)
        cls.ingredient = Ingredient.objects.create(
            name='kakaxa',
            measure='kg'
        )
        bulk_ingredient = []
        fields = ('name', 'measure')
        for i in range(1, 61):
            data = (f'ingredient{i}', 'kg')
            data_for_create = dict(zip(fields, data))
            ingredient = Ingredient(**data_for_create)
            bulk_ingredient.append(ingredient)
        Ingredient.objects.bulk_create(bulk_ingredient)
        bulk_recipe = []
        fields = ('author', 'name', 'text', 'cooking_time')
        for i in range(2, 20):
            data = (CustomUser.objects.get(pk=i), f'Recipe{i}', 'Text{i}', i)
            data_for_create = dict(zip(fields, data))
            recipe = Recipe(**data_for_create)
            bulk_recipe.append(recipe)
        Recipe.objects.bulk_create(bulk_recipe)
        for i in Recipe.objects.all():
            Quantity.objects.create(
                recipe=i,
                ingredient=Ingredient.objects.get(pk=i.pk),
                amount=100
            )
            Quantity.objects.create(
                recipe=i,
                ingredient=Ingredient.objects.get(pk=i.pk + 1),
                amount=150
            )
            ingredients = (Ingredient.objects.get(pk=i.pk).pk,
                           Ingredient.objects.get(pk=i.pk+1).pk)
            i.ingredients.set(ingredients)
            i.tags.set(Tag.objects.filter(pk=cls.tag.pk))

    def setUp(self):
        user = CustomUser.objects.first()
        self.auth_client = Client()
        self.auth_client.force_login(user)

    def test_anon_get(self):
        """
        Доступность страниц для анонимного пользователя
        """
        recipe = Recipe.objects.first()
        user = CustomUser.objects.first()
        tag = Tag.objects.first()
        ingredient = Ingredient.objects.first()
        addresses = (
            ('/api/recipes/', HTTPStatus.OK),
            (f'/api/recipes/{recipe.pk}/', HTTPStatus.OK),
            (f'/api/users/{user.pk}/', HTTPStatus.OK),
            ('/api/users/', HTTPStatus.UNAUTHORIZED),
            ('/api/users/me/', HTTPStatus.UNAUTHORIZED),
            ('/api/tags/', HTTPStatus.OK),
            (f'/api/tags/{tag.pk}/', HTTPStatus.OK),
            ('/api/users/subscriptions/', HTTPStatus.UNAUTHORIZED),
            ('/api/ingredients/', HTTPStatus.OK),
            (f'/api/ingredients/{ingredient.pk}/', HTTPStatus.OK)
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


# class AuthUserTest(TestCase):

#     def test_users(self):
#         bulk_users = []
#         fields = ('first_name', 'last_name', 'username', 'email', 'password')
#         for i in range(1, 30):
#             data = (f'Name{i}', f'Surname{i}', f'username{i}',
#                     f'mail{i}@fake.fake', 'pass__word{i}')
#             data_for_create = dict(zip(fields, data))
#             user = CustomUser(**data_for_create)
#             bulk_users.append(user)
#         CustomUser.objects.bulk_create(bulk_users)
#         auth_user = Client()
#         auth_user.force_login(CustomUser.objects.first())
#         response = auth_user.get('/api/users/')
#         print(response)


class API_Test(APITestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        bulk_users = []
        fields = ('first_name', 'last_name', 'username', 'email', 'password')
        for i in range(1, 30):
            data = (f'Name{i}', f'Surname{i}', f'username{i}',
                    f'mail{i}@fake.fake', 'pass__word{i}')
            data_for_create = dict(zip(fields, data))
            user = CustomUser(**data_for_create)
            bulk_users.append(user)
        CustomUser.objects.bulk_create(bulk_users)
        cls.tag = Tag.objects.create(
            name='test_tag_1',
            color='#000000',
            slug='slug1'
        )
        bulk_tag = []
        fields = ('name', 'color', 'slug')
        for i in range(1, 4):
            data = (f'tag{i}', f'#00000{i}', f'slug_{i}')
            data_for_create = dict(zip(fields, data))
            tag = Tag(**data_for_create)
            bulk_tag.append(tag)
        Tag.objects.bulk_create(bulk_tag)
        cls.ingredient = Ingredient.objects.create(
            name='kakaxa',
            measure='kg'
        )
        bulk_ingredient = []
        fields = ('name', 'measure')
        for i in range(1, 61):
            data = (f'ingredient{i}', 'kg')
            data_for_create = dict(zip(fields, data))
            ingredient = Ingredient(**data_for_create)
            bulk_ingredient.append(ingredient)
        Ingredient.objects.bulk_create(bulk_ingredient)
        bulk_recipe = []
        fields = ('author', 'name', 'text', 'cooking_time')
        for i in range(2, 20):
            data = (CustomUser.objects.get(pk=i), f'Recipe{i}', f'Text{i}', i)
            data_for_create = dict(zip(fields, data))
            recipe = Recipe(**data_for_create)
            bulk_recipe.append(recipe)
        Recipe.objects.bulk_create(bulk_recipe)
        for i in Recipe.objects.all():
            Quantity.objects.create(
                recipe=i,
                ingredient=Ingredient.objects.get(pk=i.pk),
                amount=100
            )
            Quantity.objects.create(
                recipe=i,
                ingredient=Ingredient.objects.get(pk=i.pk + 1),
                amount=150
            )
            ingredients = (Ingredient.objects.get(pk=i.pk).pk,
                           Ingredient.objects.get(pk=i.pk+1).pk)
            i.ingredients.set(ingredients)
            i.tags.set(Tag.objects.filter(pk=cls.tag.pk))

    def test_get(self):
        # bulk_users = []
        # fields = ('first_name', 'last_name', 'username', 'email', 'password')
        # for i in range(1, 30):
        #     data = (f'Name{i}', f'Surname{i}', f'username{i}',
        #             f'mail{i}@fake.fake', 'pass__word{i}')
        #     data_for_create = dict(zip(fields, data))
        #     user_to_list = CustomUser(**data_for_create)
        #     bulk_users.append(user_to_list)
        # CustomUser.objects.bulk_create(bulk_users)
        auth_client = APIClient()
        data = {
            'first_name': 'Jack',
            'last_name': 'Sparrow',
            'username': 'pirat',
            'email': 'pirat@fake.fake',
            'password': 'pass__word'
        }
        # Registration of new user
        response = auth_client.post(
            '/api/users/', data=data
        )
        data = {
            'email': 'pirat@fake.fake',
            'password': 'pass__word'
        }
        # login
        response = auth_client.post(
            '/api/auth/token/login/', data=data
        )
        token = response.data['auth_token']
        auth_client.credentials(HTTP_AUTHORIZATION='Token ' + token)
        # users list
        response = auth_client.get('/api/users/')
        results = ('id', 'first_name', 'last_name', 'email', 'username',
                   'is_subscribed')
        for key in response.data['results'][0].keys():
            with self.subTest(key=key):
                self.assertTrue(key in results)
        # profile user
        response = auth_client.get(
            f'/api/users/{CustomUser.objects.first().pk}/'
        )
        for key in response.data.keys():
            with self.subTest(key=key):
                self.assertTrue(key in results)
        # me
        response = auth_client.get('/api/users/me/')
        for key in response.data.keys():
            with self.subTest(key=key):
                self.assertTrue(key in results)
        # get /api/recipes/

        response = auth_client.get('/api/recipes/')
        results = ('id', 'is_in_shoppingcart', 'is_favorited', 'author',
                   'tags', 'ingredients', 'name', 'image', 'text',
                   'cooking_time')
        for key in response.data['results'][0].keys():
            with self.subTest(key=key):
                self.assertTrue(key in results)
        results_ingredients = ('id', 'ingredient', 'amount', 'mesurement_unit')
        for key in response.data['results'][0]['ingredients'][0].keys():
            with self.subTest(key=key):
                self.assertTrue(key in results_ingredients)
        results_tags = ('id', 'name', 'color', 'slug')
        for key in response.data['results'][0]['tags'][0].keys():
            with self.subTest(key=key):
                self.assertTrue(key in results_tags)
        results_author = ('id', 'first_name', 'last_name', 'email', 'username',
                          'is_subscribed')
        for key in response.data['results'][0]['author'].keys():
            with self.subTest(key=key):
                self.assertTrue(key in results_author)
