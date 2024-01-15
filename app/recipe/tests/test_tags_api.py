"""
Tests for the tags API.
"""

import os
from django import setup
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
setup()
from core.models import Tag, Recipe

from recipe.serializers import TagSerializer


TAGS_URL = reverse('recipe:tag-list')

def detail_url(tag_id):
    """Create a unique and return a tag detail url"""
    
    return reverse('recipe:tag-detail', args=[tag_id])

def create_user(email='user@example.com', password='testpass123'):
    """Create and return a user."""
    return get_user_model().objects.create_user(email, password)



class PublicTagsAPITest(TestCase):
    """Test Unauthenticated API requests."""
    
    def setUp(self):
        self.client = APIClient()
        
    def test_auth_required(self):
        """Test auth is required for retrieving tags."""
        res = self.client.get(TAGS_URL)
        
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        
        
class PrivateTagsAPITest(TestCase):
    """Test Authenticated API requests."""
    
    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)
        
    
    def test_retrieve_tags(self):
        """Test retrieving a list of tags."""
        Tag.objects.create(user=self.user, name='Dessert')
        Tag.objects.create(user=self.user, name='Christmas')
        
        res = self.client.get(TAGS_URL)
        
        tags = Tag.objects.all().order_by('-name') #order by reverse name aka descending
        serializer = TagSerializer(tags, many=True) #jsonify that list of objects!
        
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
        
        
    def test_tags_limited_to_user(self):
        """Test list of tags is limited to authenticated user."""
        user2 = create_user(email='user2@example.com')
        Tag.objects.create(user=user2, name='Vegan') #not authenticated and shouldn't be created
        tag = Tag.objects.create(user=self.user, name='Comfort Food')
        
        res = self.client.get(TAGS_URL)
        
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1) #we only send 1 tag to authenticated user
        self.assertEqual(res.data[0]['name'], tag.name)
        self.assertEqual(res.data[0]['id'], tag.id)
        
    def test_update_tag(self):
        """Test updating a tag."""
        tag = Tag.objects.create(user=self.user, name='Christmas')
        
        payload = {'name' : 'Dessert'}
        url = detail_url(tag.id)
        res = self.client.patch(url, payload) 
        
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        tag.refresh_from_db()
        self.assertEqual(tag.name, payload['name'])
        
    def test_delete_tag(self):
        """Test deleting a tag."""
        tag = Tag.objects.create(user=self.user, name='Breakfast')
        
        url = detail_url(tag.id)
        res = self.client.delete(url)
        
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        tags = Tag.objects.filter(user=self.user)
        self.assertFalse(tags.exists())
        
        
    def test_filter_tags_assigned_to_recipe(self):
        """Test only listing tags assigned to recipes."""
        
        tag1 = Tag.objects.create(user=self.user, name='Cajun')
        tag2 = Tag.objects.create(user=self.user, name='Southern')
        recipe = Recipe.objects.create(
            title='Gumbo',
            time_minutes=5,
            price = '5.50',
            user=self.user
        )
        recipe.tags.add(tag1)
        
        res = self.client.get(TAGS_URL, {'assigned_only': 1})
        
        s1 = TagSerializer(tag1)
        s2 = TagSerializer(tag2)
        self.assertIn(s1.data, res.data)
        self.assertNotIn(s2.data, res.data)
        
        
    def test_filtered_tags_unique(self):
        """Test filtered tags returned to unique list."""
        tag1 = Tag.objects.create(user=self.user, name='Breakfast')
        Tag.objects.create(user=self.user, name='Southern')
        recipe1 = Recipe.objects.create(
            title='Eggs Benedict',
            time_minutes=60,
            price='5.50',
            user=self.user
        )
        recipe2 = Recipe.objects.create(
            title='Eggs Scrambled',
            time_minutes=60,
            price='5.50',
            user=self.user
        )
        
        recipe1.tags.add(tag1)
        recipe2.tags.add(tag1)
        
        res = self.client.get(TAGS_URL, {'assigned_only': 1})
        
        self.assertEqual(len(res.data),1)