from rest_framework.viewsets import ModelViewSet

from core.models import Ingredient, Recipe
from recipe import serializers


class IngredientViewSet(ModelViewSet):
    """Manage ingredients in the database"""
    queryset = Ingredient.objects.all()
    serializer_class = serializers.IngredientSerializer

    def get_queryset(self):
        """Return objects for the current authenticated user only"""
        assigned_only = bool(
            int(self.request.query_params.get('assigned_only', 0))
        )
        queryset = self.queryset
        if assigned_only:
            queryset = queryset.filter(recipe__isnull=False)\
                                .order_by('-name').distinct()

        return queryset

    def get_serializer_class(self):
        """Return serializer class"""
        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new recipe"""
        serializer.save()


class RecipeViewSet(ModelViewSet):
    """Manage recipes in the database"""
    queryset = Recipe.objects.all()
    serializer_class = serializers.RecipeSerializer

    def get_queryset(self):
        """Retrieve the recipes"""
        queryset = Recipe.objects.all()
        names = self.request.query_params.get('name')
        if names:
            queryset = queryset.filter(name__startswith=names)
        return queryset

    def get_serializer_class(self):
        """Return serializer class"""
        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new recipe"""
        serializer.save()
