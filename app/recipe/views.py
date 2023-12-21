"""
Views for the recipe APIs.
"""

from rest_framework import viewsets, mixins 
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Recipe, Tag
from recipe import serializers 


class RecipeViewSet(viewsets.ModelViewSet):
    """View for manage recipe APIs."""
    serializer_class = serializers.RecipeDetailSerializer
    queryset = Recipe.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Retrieve recipes for authenticated user."""
        return self.queryset.filter(user=self.request.user).order_by('-id')
    
    def get_serializer_class(self):
        """Return the serializer class for request."""
        if self.action == 'list': #calling the HTTP GET request to this endpoint it will be a 'list' action
            return serializers.RecipeSerializer 
        
        return self.serializer_class
    
    def perform_create(self, serializer):
        """Create a new recipe."""
        serializer.save(user=self.request.user) #new recipess created are saved to the current authenticated user


class TagViewSet(mixins.UpdateModelMixin, 
                mixins.DestroyModelMixin,
                viewsets.GenericViewSet,
                mixins.ListModelMixin):
    """Manage tags in the database."""
    serializer_class = serializers.TagSerializer
    queryset = Tag.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filter querset to authenticated user."""
        return self.queryset.filter(user=self.request.user).order_by('-name')