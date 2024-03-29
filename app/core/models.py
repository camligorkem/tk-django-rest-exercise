from django.db import models


class Recipe(models.Model):
    """Recipe object"""
    name = models.CharField(max_length=255)
    description = models.TextField()

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Ingredient to be used in a recipe"""
    name = models.CharField(max_length=255)
    recipe = models.ForeignKey(
        'Recipe',
        on_delete=models.CASCADE,
        null=True,
        related_name='ingredients',
    )

    def __str__(self):
        return self.name
