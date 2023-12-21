"""
Serializers for the user API view.
"""

from django.contrib.auth import (
    get_user_model,
    authenticate,
)
from django.utils.translation import gettext as _

from rest_framework import serializers

#json input from API, validates to make sure it is secure & correct & converts to python dictionary
#or object for the database
class UserSerializer(serializers.ModelSerializer):
    """Serializer for the user object."""
    
    class Meta: 
        #tell django rest_framework what model this serializer is for and what fields are provided 
        #in requests that need to be saved in model created 
        model = get_user_model()
        fields = ['email', 'password', 'name'] #only use fields that users can change through api
        extra_kwargs = {'password': {'write_only': True, 'min_length': 5}} #extra data about rules
        
        
    def create(self, validated_data):
        """Create and return a user with encrypted password"""
        return get_user_model().objects.create_user(**validated_data)
    
    def update(self, instance, validated_data):
        """Update and return user."""
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data) #using the update method on the ModelSerializer method
        
        if password:
            user.set_password(password)
            user.save()
            
        return user
    

class AuthTokenSerializer(serializers.Serializer):
    """Serializer for the user auth token."""
    email = serializers.EmailField()
    password = serializers.CharField(style={'input_type': 'password'}, trim_whitespace=False)
    

    def validate(self, attrs):
        """Validate and authenticate the user."""
        email = attrs.get('email')
        password = attrs.get('password')
        user = authenticate(
            requests = self.context.get('request'),
            username=email,
            password=password
        )
        if not user:
            msg = _('Unable to authenticate with provided credentials.')
            raise serializers.ValidationError(msg, code='authorization')
        
        attrs['user'] = user
        return attrs