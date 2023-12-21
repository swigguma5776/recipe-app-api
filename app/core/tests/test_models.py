"""
Tests for models.
"""

from decimal import Decimal 
from django.test import TestCase
from django.contrib.auth import get_user_model

#using other models sbesides user models we will need to import directly
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