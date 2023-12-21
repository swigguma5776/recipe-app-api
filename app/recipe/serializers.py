"""
Serializers for recipe APIs
"""

from rest_framework import serializers

from core.models import Recipe, Tag


class TagSerializer(serializers.ModelSerializer):
    """Serializer for tags."""
    
    class Meta:
        model = Tag
        fields = ['id', 'name']
        read_only_fields = ['id']
        

class RecipeSerializer(serializers.ModelSerializer):
    """Serializers for recipes."""
    tags = TagSerializer(many=True, required=False)
    
    class Meta:
        model = Recipe
        fields = ['id', 'title', 'time_minutes', 'price', 'link', 'tags']
        read_only_fields = ['id']
        
    def _get_or_create_tags(self, tags, recipe):
        """Handle getting or creating tags as needed"""
        auth_user = self.context['request'].user #authenticated user from the request
        for tag in tags:
            tag_obj, created = Tag.objects.get_or_create( #helper method if it exists itll just get, if it doesnt it will create
                user=auth_user,
                **tag #grabs all key/value pairs for tag 
            )
            recipe.tags.add(tag_obj)
            
            
        
    def create(self, validated_data): #overide the create logic
        """Create a recipe."""
        tags = validated_data.pop('tags', []) #remove the key/value pair from dictionary
        recipe = Recipe.objects.create(**validated_data) #create a new recipe without tag since tags does not exist on Recipe object
        self._get_or_create_tags(tags, recipe)
        
        return recipe
    
    def update(self, instance, validated_data):
        """Update recipe."""
        tags = validated_data.pop('tags', None)
        
        if tags is not None:
            instance.tags.clear()
            self._get_or_create_tags(tags, instance)
            
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
            
        instance.save()
        return instance
        
        
class RecipeDetailSerializer(RecipeSerializer):
    """Serializer for the recipe detail view."""
    
    class Meta(RecipeSerializer.Meta):
        fields = RecipeSerializer.Meta.fields + ['description']
        
        
