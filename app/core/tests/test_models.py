from django.test import TestCase

from core import models


class ModelTests(TestCase):

    def test_recipe_str(self):
        """Test the recipe string representation"""
        recipe = models.Recipe.objects.create(
            name='Steak and Mushroom Sauce',
            description='Bla bla bla',
        )
        self.assertEqual(str(recipe), recipe.name)

    def test_ingredient_str(self):
        """Test the ingredient string representation"""
        ingredient = models.Ingredient.objects.create(
            name='Chocolate',
        )
        self.assertEqual(str(ingredient), ingredient.name)
