"""
Tests for models.
"""

from unittest.mock import patch
from decimal import Decimal 
from django.test import TestCase
from django.contrib.auth import get_user_model

#using other models sbesides user models we will need to import directly
import os
from django import setup

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
setup()

from core import models

def create_user(email='user@example.com', password='testpass123'):
    """Creaate and return new user"""
    return get_user_model().objects.create_user(email, password)

class ModelTest(TestCase):
    """
    Test models.
    """
    
    def test_create_user_with_email_successful(self):
        """Test creating user with an email is successful"""
        email = "test@example.com"
        password = "testpass123"
        user = get_user_model().objects.create_user(email=email,password=password)
        
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))
        
        
    def test_new_user_email_normalized(self):
        """Test email is normalized for new users"""
        sample_emails = [
            ['test1@EXAMPLE.com', 'test1@example.com'],
            ['Test2@Example.com', 'Test2@example.com'],
            ['TEST3@EXAMPLE.COM', 'TEST3@example.com'],
            ['test4@example.COM', 'test4@example.com']
        ]
        
        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(email, 'sample123')
            self.assertEqual(user.email, expected)
            
            
    def test_new_user_without_email_raises_error(self):
        """Test that creating user without an email raises a ValueError"""
        
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user("", "sample123")
            
            
    def test_create_superuser(self):
        """Test creating a superuser."""
        user = get_user_model().objects.create_superuser('test@example.com', 'sample123')
        
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
        
    def test_create_recipe(self):
        """Test creating a recipe is successful."""
        
        user = get_user_model().objects.create_user(
            'test@example.com',
            'testpass123'
        )
        
        recipe = models.Recipe.objects.create(
            user=user,
            title='Really cool recipe',
            time_minutes=30,
            price=Decimal('5.50'), #Decimal is more accurate
            description='It is the coolest recipe ever made.'
        )
        
        self.assertEqual(str(recipe), recipe.title)
        
    def test_create_tag(self):
        """Test creaataing a tag is successsful."""
        user = create_user()
        tag = models.Tag.objects.create(user=user, name='Tag1')
        
        self.assertEqual(str(tag), tag.name)
        
    def test_create_ingredient(self):
        """Test creating an ingredient is successful."""
        user = create_user()
        ingredient = models.Ingredient.objects.create(
            user=user,
            name='Ingredient1'
        )
        
        self.assertEqual(str(ingredient), ingredient.name)
        
    @patch('core.models.uuid.uuid4') #mocking creating a unique id
    def test_recipe_file_name_uuid(self, mock_uuid):
        """Test generating image path."""
        uuid = 'test-uuid' #mocked response
        mock_uuid.return_value = uuid
        file_path = models.recipe_image_file_path(None, 'example.jpg')
        
        self.assertEqual(file_path, f"uploads/recipe/{uuid}.jpg")