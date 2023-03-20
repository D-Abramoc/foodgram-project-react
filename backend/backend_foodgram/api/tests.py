from http import HTTPStatus
from io import TextIOWrapper

from recipes.models import (Tag, Recipe, Ingredient, Quantity)
from users.models import CustomUser
from rest_framework.test import APITestCase, APIClient
from rest_framework.authtoken.models import Token


KEYS = {
    'user': ('id', 'first_name', 'last_name', 'email', 'username',
             'is_subscribed'),
    'recipe': ('id', 'is_in_shopping_cart', 'is_favorited', 'author',
               'tags', 'ingredients', 'name', 'image', 'text',
               'cooking_time'),
    'recipe_ingredients': ('id', 'ingredient', 'amount', 'mesurement_unit'),
    'recipe_tags': ('id', 'name', 'color', 'slug')
}


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
        self.assertEqual(len(response_keys), len(expected_keys))
        for key in response_keys:
            with self.subTest(key=key):
                self.assertTrue(key in expected_keys)

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
        Token.objects.all().delete()
        number_of_users = CustomUser.objects.count()
        data = {
            'first_name': 'Gector',
            'last_name': 'Barbossa',
            'username': 'pirat_too',
            'email': 'pirat_too@fake.fake',
            'password': 'pass__word'
        }
        # Registration of new user
        response = self.client.post(
            '/api/users/', data=data
        )
        self.assertEqual(CustomUser.objects.count(), number_of_users + 1)
        data = {
            'email': 'pirat_too@fake.fake',
            'password': 'pass__word'
        }
        # login
        response = self.client.post(
            '/api/auth/token/login/', data=data
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(Token.objects.count(), 1)

    def test_get_users(self):
        response = self.auth_client.get('/api/users/')
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.check_keys(response.data['results'][0].keys(), KEYS['user'])
        self.assertEqual(len(response.data['results'][0].keys()),
                         len(KEYS['user']))
        self.assertEqual(response.data['count'], CustomUser.objects.count())
        self.assertEqual(response.data['next'],
                         'http://testserver/api/users/?page=2')
        self.assertEqual(response.data['previous'], None)
        self.assertEqual(len(response.data['results']), 6)
        # page and limit
        response = self.auth_client.get('/api/users/?page=3&limit=2')
        self.assertEqual(response.data['count'], CustomUser.objects.count())
        self.assertEqual(response.data['next'],
                         'http://testserver/api/users/?limit=2&page=4')
        self.assertEqual(response.data['previous'],
                         'http://testserver/api/users/?limit=2&page=2')
        self.assertEqual(len(response.data['results']), 2)
        # profile user
        response = self.auth_client.get(
            f'/api/users/{CustomUser.objects.first().pk}/'
        )
        self.check_keys(response.data.keys(), KEYS['user'])
        self.assertEqual(len(response.data.keys()), len(KEYS['user']))

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
        self.assertEqual(response.data['count'], Recipe.objects.count())
        self.assertEqual(response.data['next'],
                         'http://testserver/api/recipes/?page=2')
        self.assertEqual(response.data['previous'], None)
        self.assertEqual(len(response.data['results']), 6)
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
        '''
        Test post and delete recipe.
        '''
        # post recipe, valid data
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
        response = self.auth_client.delete(
            f'/api/recipes/{Recipe.objects.first().pk}/'
        )
        self.assertEqual(Recipe.objects.count(), 0)
        # post recipe, invalid data
        Recipe.objects.all().delete()
        invalid_data = (
            {
                'tags': [1],
                'name': 'Name',
                'text': 'text',
                'cooking_time': 15,
                'image': ('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEA'
                          'AAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACX'
                          'BIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOy'
                          'YQAAAABJRU5ErkJggg=='),
            },
            {
                'ingredients': [{'id': 1, 'amount': 15}],
                'name': 'Name',
                'text': 'text',
                'cooking_time': 15,
                'image': ('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEA'
                          'AAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACX'
                          'BIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOy'
                          'YQAAAABJRU5ErkJggg=='),
            },
            {
                'ingredients': [{'id': 1, 'amount': 15}],
                'tags': [1],
                'text': 'text',
                'cooking_time': 15,
                'image': ('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEA'
                          'AAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACX'
                          'BIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOy'
                          'YQAAAABJRU5ErkJggg=='),
            },
            {
                'ingredients': [{'id': 1, 'amount': 15}],
                'tags': [1],
                'name': 'Name',
                'cooking_time': 15,
                'image': ('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEA'
                          'AAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACX'
                          'BIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOy'
                          'YQAAAABJRU5ErkJggg=='),
            },
            {
                'ingredients': [{'id': 1, 'amount': 15}],
                'tags': [1],
                'name': 'Name',
                'text': 'text',
                'image': ('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEA'
                          'AAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACX'
                          'BIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOy'
                          'YQAAAABJRU5ErkJggg=='),
            },
            {
                'ingredients': [{'id': 1, 'amount': 15}],
                'tags': [1],
                'name': 'Name',
                'text': 'text',
                'cooking_time': 15,
            },
            {
                'ingredients': 1,
                'tags': [1],
                'name': 'Name',
                'text': 'text',
                'cooking_time': 15,
                'image': ('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEA'
                          'AAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACX'
                          'BIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOy'
                          'YQAAAABJRU5ErkJggg=='),
            },
            {
                'ingredients': 'string',
                'tags': [1],
                'name': 'Name',
                'text': 'text',
                'cooking_time': 15,
                'image': ('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEA'
                          'AAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACX'
                          'BIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOy'
                          'YQAAAABJRU5ErkJggg=='),
            },
            {
                'ingredients': {'id': 1, 'amount': 15},
                'tags': [1],
                'name': 'Name',
                'text': 'text',
                'cooking_time': 15,
                'image': ('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEA'
                          'AAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACX'
                          'BIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOy'
                          'YQAAAABJRU5ErkJggg=='),
            },
            {
                'ingredients': [{'id': 5000, 'amount': 15}],
                'tags': [1],
                'name': 'Name',
                'text': 'text',
                'cooking_time': 15,
                'image': ('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEA'
                          'AAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACX'
                          'BIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOy'
                          'YQAAAABJRU5ErkJggg=='),
            },
            {
                'ingredients': [{'id': 1, 'amount': -15}],
                'tags': [1],
                'name': 'Name',
                'text': 'text',
                'cooking_time': 15,
                'image': ('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEA'
                          'AAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACX'
                          'BIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOy'
                          'YQAAAABJRU5ErkJggg=='),
            },
            {
                'ingredients': [],
                'tags': [1],
                'name': 'Name',
                'text': 'text',
                'cooking_time': 15,
                'image': ('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEA'
                          'AAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACX'
                          'BIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOy'
                          'YQAAAABJRU5ErkJggg=='),
            },
            {
                'ingredients': [{'id': 1, 'amount': 15}],
                'tags': 1,
                'name': 'Name',
                'text': 'text',
                'cooking_time': 15,
                'image': ('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEA'
                          'AAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACX'
                          'BIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOy'
                          'YQAAAABJRU5ErkJggg=='),
            },
            {
                'ingredients': [{'id': 1, 'amount': 15}],
                'tags': [1],
                'name': 1,
                'text': 'text',
                'cooking_time': 15,
                'image': ('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEA'
                          'AAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACX'
                          'BIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOy'
                          'YQAAAABJRU5ErkJggg=='),
            },
            {
                'ingredients': [{'id': 1, 'amount': 15}],
                'tags': [1],
                'name': 'Name',
                'text': 1,
                'cooking_time': 15,
                'image': ('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEA'
                          'AAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACX'
                          'BIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOy'
                          'YQAAAABJRU5ErkJggg=='),
            },
            {
                'ingredients': [{'id': 1, 'amount': 15}],
                'tags': [1],
                'name': 'Name',
                'text': 'text',
                'cooking_time': -15,
                'image': ('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEA'
                          'AAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACX'
                          'BIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOy'
                          'YQAAAABJRU5ErkJggg=='),
            },
            {
                'ingredients': [{'id': 1, 'amount': 15}],
                'tags': [1],
                'name': 'Name',
                'text': 'text',
                'cooking_time': 15,
                'image': 1,
            },
            {
                'ingredients': [{'id': 1, 'amount': 15}],
                'tags': [12],
                'name': 'Name',
                'text': 'text',
                'cooking_time': 15,
                'image': ('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEA'
                          'AAABAgMAAABieywaAAAACVBMVEUAAAD///9fX1/S0ecCAAAACX'
                          'BIWXMAAA7EAAAOxAGVKw4bAAAACklEQVQImWNoAAAAggCByxOy'
                          'YQAAAABJRU5ErkJggg=='),
            },
        )
        for data in invalid_data:
            with self.subTest(data=data):
                response = self.auth_client.post(
                    '/api/recipes/', data=data, format='json'
                )
                self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)
                self.assertEqual(Recipe.objects.count(), 0)

    def test_subscriptions(self):
        Recipe.objects.create(
            author=CustomUser.objects.get(username__endswith='name2'),
            name='Name 22',
            text='Text 22',
            cooking_time=2
        )
        for user in CustomUser.objects.filter(username__endswith='2'):
            response = self.auth_client.post(
                f'/api/users/{user.pk}/subscribe/'
            )
        # TODO check response when subscribe
        for user in CustomUser.objects.filter(username__endswith='3'):
            response = self.auth_client.post(
                f'/api/users/{user.pk}/subscribe/'
            )
        response = self.auth_client.get(
            '/api/users/subscriptions/?limit=6&recipes_limit=2'
        )
        token = response.request['HTTP_AUTHORIZATION'].split()[1]
        current_user = Token.objects.get(key=token).user
        self.assertEqual(current_user.authors.count(), 6)
        self.auth_client.delete(
            f'/api/users/{current_user.authors.first().author.pk}/subscribe/'
        )
        self.assertEqual(current_user.authors.count(), 5)

    def test_me(self):
        response = self.auth_client.get('/api/users/me/')
        self.check_keys(response.data.keys(), KEYS['user'])

    def test_recipes_filter(self):
        self.auth_client.post('/api/recipes/5/favorite/')
        self.auth_client.post('/api/recipes/5/shopping_cart/')
        self.auth_client.post('/api/users/6/subscribe/')
        response = self.auth_client.get('/api/recipes/?is_favorited=1')
        for result in response.data['results']:
            with self.subTest(result=result):
                self.assertEqual(result['is_favorited'], True)
        response = self.auth_client.get('/api/recipes/?is_favorited=0')
        for result in response.data['results']:
            with self.subTest(result=result):
                self.assertEqual(result['is_favorited'], False)
        response = self.auth_client.get('/api/recipes/?is_in_shopping_cart=1')
        for result in response.data['results']:
            with self.subTest(result=result):
                self.assertEqual(result['is_in_shopping_cart'], True)
        response = self.auth_client.get('/api/recipes/?is_in_shopping_cart=0')
        for result in response.data['results']:
            with self.subTest(result=result):
                self.assertEqual(result['is_in_shopping_cart'], False)

    def test_recipe_patch(self):
        ...

    def test_shopping_cart(self):
        # add to shopping_cart
        response = self.auth_client.post('/api/recipes/1/shopping_cart/')
        token = response.request['HTTP_AUTHORIZATION'].split()[1]
        current_user = Token.objects.get(key=token).user
        self.assertEqual(current_user.shoppingcart.recipes.count(), 1)
        response = self.auth_client.post('/api/recipes/2/shopping_cart/')
        self.assertEqual(current_user.shoppingcart.recipes.count(), 2)
        # download shopping_cart
        response = self.auth_client.get('/api/recipes/download_shopping_cart/')
        self.assertIsInstance(response.data, TextIOWrapper)
        # remove record from shopping_cart
        response = self.auth_client.delete('/api/recipes/1/shopping_cart/')
        self.assertEqual(current_user.shoppingcart.recipes.count(), 1)

    def test_in_out_favorite(self):
        response = self.auth_client.post('/api/recipes/5/favorite/')
        token = response.request['HTTP_AUTHORIZATION'].split()[1]
        current_user = Token.objects.get(key=token).user
        self.assertEqual(current_user.favorite_recipes.count(), 1)
        response = self.auth_client.delete('/api/recipes/5/favorite/')
        self.assertEqual(current_user.favorite_recipes.count(), 0)

    def test_filter_ingredients(self):
        ...

    def test_logout(self):
        self.auth_client.post('/api/auth/token/logout/')
        self.assertEqual(Token.objects.count(), 0)

    def test_password(self):
        current_password = CustomUser.objects.get(username='pirat').password
        data = {
            'current_password': 'pass__word',
            'new_password': 'pass__word1'
        }
        self.auth_client.post('/api/users/set_password/', data=data)
        new_password = CustomUser.objects.get(username='pirat').password
        self.assertFalse(current_password == new_password)
