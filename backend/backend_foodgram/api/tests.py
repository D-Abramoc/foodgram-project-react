from http import HTTPStatus

from django.test import TestCase, Client
import json
from recipes.models import (Tag, Recipe, Ingredient, Quantity)
from users.models import CustomUser
from rest_framework.test import APITestCase, APIClient


KEYS = {
    'user': ('id', 'first_name', 'last_name', 'email', 'username',
             'is_subscribed'),
    'recipe': ('id', 'is_in_shoppingcart', 'is_favorited', 'author',
               'tags', 'ingredients', 'name', 'image', 'text',
               'cooking_time'),
    'recipe_ingredients': ('id', 'ingredient', 'amount', 'mesurement_unit'),
    'recipe_tags': ('id', 'name', 'color', 'slug')
}


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

    def setUp(self):
        self.auth_client = APIClient()
        data = {
            'first_name': 'Jack',
            'last_name': 'Sparrow',
            'username': 'pirat',
            'email': 'pirat@fake.fake',
            'password': 'pass__word'
        }
        # Registration of new user
        response = self.auth_client.post(
            '/api/users/', data=data
        )
        data = {
            'email': 'pirat@fake.fake',
            'password': 'pass__word'
        }
        # login
        response = self.auth_client.post(
            '/api/auth/token/login/', data=data
        )
        token = response.data['auth_token']
        self.auth_client.credentials(HTTP_AUTHORIZATION='Token ' + token)

    def check_keys(self, response_keys, expected_keys):
        for key in response_keys:
            with self.subTest(key=key):
                self.assertTrue(key in expected_keys)

    def test_get_users(self):
        response = self.auth_client.get('/api/users/')
        self.check_keys(response.data['results'][0].keys(), KEYS['user'])
        # profile user
        response = self.auth_client.get(
            f'/api/users/{CustomUser.objects.first().pk}/'
        )
        self.check_keys(response.data.keys(), KEYS['user'])
        # me
        response = self.auth_client.get('/api/users/me/')
        self.check_keys(response.data.keys(), KEYS['user'])

    def test_recipes(self):
        # get /api/recipes/
        response = self.auth_client.get('/api/recipes/')
        self.check_keys(response.data['results'][0].keys(), KEYS['recipe'])
        self.check_keys(response.data['results'][0]['ingredients'][0].keys(),
                        KEYS['recipe_ingredients'])
        self.check_keys(response.data['results'][0]['tags'][0].keys(),
                        KEYS['recipe_tags'])
        self.check_keys(response.data['results'][0]['author'].keys(),
                        KEYS['user'])
        # get /api/recipes/<id>/
        response = self.auth_client.get(
            f'/api/recipes/{Recipe.objects.last().pk}/'
        )
        self.check_keys(response.data.keys(), KEYS['recipe'])
        self.check_keys(response.data['author'].keys(), KEYS['user'])
        self.check_keys(response.data['tags'][0].keys(), KEYS['recipe_tags'])
        self.check_keys(response.data['ingredients'][0].keys(),
                        KEYS['recipe_ingredients'])

    def test_create_delete_recipe(self):
        # post recipe, delete recipe
        Recipe.objects.all().delete()
        data = {
            'ingredients': [{'id': 1, 'amount': 15}],
            'tags': [1],
            'name': 'Name',
            'text': 'text',
            'cooking_time': 15,
            'image': ('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABA'
                      'gMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACXBIWXMAAA7E'
                      'AAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOyYQAAAABJRU5ErkJ'
                      'ggg=='),
        }
        response = self.auth_client.post(
            '/api/recipes/', data=data, format='json'
        )
        self.check_keys(response.data.keys(), KEYS['recipe'])
        self.assertEqual(Recipe.objects.count(), 1)
        # delete recipe
        response = self.auth_client.delete(f'/api/recipes/{Recipe.objects.first()}/')
        self.assertEqual(Recipe.objects.count(), 0)
