
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe, Ingredient

from recipe.serializers import RecipeSerializer

RECIPES_URL = reverse('recipe:recipe-list')


def detail_url(recipe_id):
    """Return Recipe detail URL"""
    return reverse('recipe:recipe-detail', args=[recipe_id])


def sample_ingredient(name='Cinnamon'):
    """Create and return a sample ingredient"""
    return Ingredient.objects.create(name=name)


def sample_recipe(name='Sample Recipe', description='Insert Description Here'):
    """Create and return sample recipe"""
    return Recipe.objects.create(name=name, description=description)


class RecipeApiTests(TestCase):
    """Test unauthenticated recipe API access"""
    def setUp(self):
        self.client = APIClient()

    def test_retrieve_recipes(self):
        """Test retrieving a list of the recipes"""
        sample_recipe(name='Recipe 1')
        sample_recipe(name='Recipe 2')

        res = self.client.get(RECIPES_URL)
        recipes = Recipe.objects.all()
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_recipe_succesful(self):
        """Test creating recipe"""
        payload = {
            'name': 'Chocolate cheesecake',
            'description': 'It takes x minute to cook',
            "ingredients": [
                {"name": "dough"}, {"name": "cheese"}, {"name": "tomato"}]
        }

        res = self.client.post(RECIPES_URL, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        serializer = RecipeSerializer(recipe)
        self.assertEqual(serializer.data, res.data)

    def test_create_recipe_unsuccesful(self):
        """Test creating recipe unsucessful"""
        payload = {
            'name': '',
            'description': '',
        }
        res = self.client.post(RECIPES_URL, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_recipe_without_ingredients(self):
        """Test creating a recipe without ingredients"""
        payload = {
            'name': 'Pasta with tomato sauce',
            'description': 'Bla bla description for tomato sauce',
            'ingredients': []
        }
        res = self.client.post(RECIPES_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        ingredients = recipe.ingredients.all()
        self.assertEqual(ingredients.count(), 0)

    def test_create_recipe_with_ingredients(self):
        """Test creating a recipe with ingredients"""
        ing_names = ['Tomato', 'Pasta']
        payload = {
            'name': 'Pasta with tomato sauce',
            'description': 'Bla bla description for tomato sauce',
            'ingredients': [{'name': ing_names[0]}, {'name': ing_names[1]}]
        }
        res = self.client.post(RECIPES_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        ingredients = recipe.ingredients.all()
        self.assertEqual(ingredients.count(), 2)
        self.assertIn(ingredients[0].name, ing_names)
        self.assertIn(ingredients[1].name, ing_names)

        self.assertEqual(payload['name'], res.data['name'])
        self.assertEqual(payload['description'], res.data['description'])

    def test_partial_update_recipe(self):
        """Test updating the recipe with patch"""
        recipe = sample_recipe()
        payload = {'name': 'Lemonade', 'ingredients': [{'name': 'Lemon'}]}

        url = detail_url(recipe.id)
        self.client.patch(url, payload, format='json')

        recipe.refresh_from_db()
        self.assertEqual(recipe.name, payload['name'])
        ingredients = recipe.ingredients.all()
        self.assertEqual(len(ingredients), 1)

    def test_full_update_recipe(self):
        """Test updating the recipe with put"""
        recipe = sample_recipe()
        payload = {
            'name': 'Spaghetti Carbonara',
            'description': 'Description for Spaghetti Carbonara .....',
            'ingredients': [{'name': 'pasta'}]
        }

        url = detail_url(recipe.id)
        self.client.put(url, payload, format="json")

        recipe.refresh_from_db()
        self.assertEqual(recipe.name, payload['name'])
        self.assertEqual(recipe.description, payload['description'])
        ingredients = recipe.ingredients.all()
        self.assertEqual(len(ingredients), 1)

    def test_filter_recipes_by_name_starts_with(self):
        """
        Tests that view is filtering the view
        by name starting with substring
        """
        recipe1 = sample_recipe(name='Toast')
        recipe2 = sample_recipe(name='Chicken cacciatore')
        recipe3 = sample_recipe(name='Chicken curry')

        res = self.client.get(
            RECIPES_URL,
            {'name': 'Chic'}
         )

        serializer1 = RecipeSerializer(recipe1)
        serializer2 = RecipeSerializer(recipe2)
        serializer3 = RecipeSerializer(recipe3)
        self.assertNotIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertIn(serializer3.data, res.data)

    def test_delete_recipe_successful(self):
        """ Test that recipe deletes succesfully
        and returns HTTP 204 No Content"""
        payload = {
            'name': 'Pasta with tomato sauce',
            'description': 'Bla bla description for tomato sauce',
            'ingredients': []
        }
        res = self.client.post(RECIPES_URL, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        # delete the above created recipe
        url = detail_url(res.data['id'])
        del_res = self.client.delete(url)
        self.assertEqual(del_res.status_code, status.HTTP_204_NO_CONTENT)

        with self.assertRaises(Recipe.DoesNotExist):
            Recipe.objects.get(id=res.data['id'])
