from rest_framework import serializers

from core.models import Ingredient, Recipe


class IngredientSerializer(serializers.ModelSerializer):
    """Serializers for ingredient objects"""

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeSerializer(serializers.ModelSerializer):
    """Serializers for recipe objects"""
    ingredients = IngredientSerializer(many=True)

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'description', 'ingredients')
        read_only_fields = ('id',)

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        for ing in ingredients:
            Ingredient.objects.get_or_create(recipe=recipe, **ing)
        recipe.save()
        recipe.refresh_from_db()
        return recipe

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.description = validated_data.get('description',
                                                  instance.description)

        # we should delete all the previous ingredients
        # and put the new one(s) if updated.
        ingredients = validated_data.pop('ingredients', [])
        recipe = super().update(instance, validated_data)
        if ingredients:
            recipe.ingredients.all().delete()
            for ing_data in ingredients:
                ingredient = Ingredient.objects.create(name=ing_data['name'])
                recipe.ingredients.add(ingredient)
        instance.save()
        recipe.save()
        recipe.refresh_from_db()
        return recipe
