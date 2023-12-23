"""
Tests for recipe API.
"""

from decimal import Decimal
import tempfile
import os

from PIL import Image

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe, Tag, Ingredient

from recipe.serializers import (
    RecipeSerializer,
    RecipeDetailSerializer,
)

RECIPES_URL = reverse('recipe:recipe-list')

#instead of just having a value as the url endpoint we need to be able to pass in the id
#to the endpoint so thats why we make a function for this endpoint.
def detail_url(recipe_id):
    """Create and return a recipe detail URL."""
    return reverse('recipe:recipe-detail', args=[recipe_id])

def image_upload_url(recipe_id):
    """Create and return an image upload URL."""
    return reverse('recipe:recipe-upload-image', args=[recipe_id]) #will call upon the upload_image function we made in our models

def create_recipe(user, **params):
    """Create and return a sample recipe."""
    defaults = {
        'title': 'Best Recipe',
        'time_minutes': 30,
        'price': Decimal('5.50'),
        'description': 'Best recipe ever description',
        'link': 'http://example.com/recipe.pdf'
    }
    defaults.update(params)
    
    recipe = Recipe.objects.create(user=user, **defaults)
    return recipe 


def create_user(**params):
    """Create and return a new user."""
    return get_user_model().objects.create_user(**params)

class PublicRecipeAPITests(TestCase):
    """Test unauthenticated API requests."""
    
    def setUp(self):
        self.client = APIClient()
        
    def test_auth_required(self):
        """Test auth is required to call API."""
        res = self.client.get(RECIPES_URL)
        
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        
class PrivateRecipeAPITests(TestCase):
    """Test authenticated API requests."""
    
    def setUp(self):
        self.client = APIClient()
        self.user = create_user(email='user@example.com', password='testpass123')
        self.client.force_authenticate(self.user)
        
    def test_retrieve_recipes(self):
        """Test retrieving a list of recipes."""
        
        create_recipe(user=self.user)
        create_recipe(user=self.user)
        
        res = self.client.get(RECIPES_URL)
        
        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
        
    def test_recipe_list_limited_to_user(self):
        """Test list of recipes is limited to authenticated user."""
        other_user = create_user(email='other@example.com', password='testpass123')
        create_recipe(user=other_user)
        create_recipe(user=self.user)
        
        res = self.client.get(RECIPES_URL)
        
        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)
        
    def test_get_recipe_detail(self):
        """Test get recipe detail."""
        recipe = create_recipe(user=self.user)
        
        url = detail_url(recipe.id)
        res = self.client.get(url)
        
        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(res.data, serializer.data)
        
    
    def test_create_recipe(self):
        """Test creating a recipe."""
        payload = {
            'title' : 'Sick of writing tests',
            'time_minutes' : 5,
            'price' : Decimal('5.99'),
        }
        
        res = self.client.post(RECIPES_URL, payload)
        
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        
        for k, v in payload.items():
            self.assertEqual(getattr(recipe, k), v)
        self.assertEqual(recipe.user, self.user)
        
        
    def test_partial_update(self):
        """Test partial update of a recipe."""
        original_link = "https://example.com/recipe.pdf"
        recipe = create_recipe(
            user=self.user,
            title='Sample Title',
            link=original_link
        )
        
        payload = {'title': 'New Recipe Title'}
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload)
        
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.link, original_link)
        self.assertEqual(recipe.user, self.user)
        
    def test_full_update(self):
        """Test full update of recipe."""

        recipe = create_recipe(
            user=self.user,
            title='Sample Title',
            description='Sample recipe description',
            link="https://example.com/recipe.pdf"
        )
        
        payload = {
            'title': 'New Recipe',
            'description': 'new description',
            'time_minutes': 10,
            'link': 'https://example.com/recipe2.pdf',
            'price': Decimal('5.50')
        }
        
        url = detail_url(recipe.id)
        res = self.client.put(url, payload)
        
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        for k,v in payload.items():
            self.assertEqual(getattr(recipe, k), v)
        self.assertEqual(recipe.user, self.user)
        
    def test_create_recipe_with_new_tags(self):
        """Test creating a recipe with new tags."""
        payload = {
            'title' : 'Grandmas Gumbo',
            'time_minutes': 60,
            'price' : Decimal('10.50'),
            'tags': [{'name': 'Southern'}, {'name': 'Cajun'}]
        }
        
        res = self.client.post(RECIPES_URL, payload, format='json')
        
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        self.assertEqual(recipe.tags.count(), 2) #make sure both tags get added
        for tag in payload['tags']: #makes sure the name gets added correctly & to the correct user
            exists = recipe.tags.filter(
                name=tag['name'],
                user=self.user
            ).exists()
            self.assertTrue(exists)
            
    def test_create_recipe_with_existing_tags(self):
        """Test creating a recipe with existing tag."""
        tag_indian = Tag.objects.create(user=self.user, name='Indian')
        payload = {
            'title': 'Pongal',
            'time_minutes': 60,
            'price' : Decimal('5.50'),
            'tags': [{'name': 'Indian'}, {'name': 'Breakfast'}]
        }
        
        res = self.client.post(RECIPES_URL, payload, format='json')
        
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        self.assertEqual(recipe.tags.count(), 2) 
        self.assertIn(tag_indian, recipe.tags.all())
        for tag in payload['tags']: #makes sure the name gets added correctly & to the correct user
            exists = recipe.tags.filter(
                name=tag['name'],
                user=self.user
            ).exists()
            self.assertTrue(exists)
            
    def test_create_tag_on_update(self):
        """Test creating tag when updating a recipe."""
        recipe = create_recipe(user=self.user)
        payload = {'tags': [{'name': 'Lunch'}]}
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')
        
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        new_tag = Tag.objects.get(user=self.user, name='Lunch')
        self.assertIn(new_tag, recipe.tags.all())
        
    def test_update_recipe_assign_tag(self):
        """Test assigning an existing tag when updating a recipe."""
        tag_breakfast = Tag.objects.create(user=self.user, name='Breakfast')
        recipe = create_recipe(user=self.user)
        recipe.tags.add(tag_breakfast)
        
        tag_lunch = Tag.objects.create(user=self.user, name='Lunch')
        payload = {'tags': [{'name': 'Lunch'}]}
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')
        
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(tag_lunch, recipe.tags.all())
        self.assertNotIn(tag_breakfast, recipe.tags.all())
        
    def test_clear_recipe_tags(self):
        """Test clearing a recipe tags"""
        tag = Tag.objects.create(user=self.user, name='Dessert')
        recipe = create_recipe(user=self.user)
        recipe.tags.add(tag)
        
        payload = {'tags': []}
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')
        
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.tags.count(), 0)
        
    def test_create_recipe_with_new_ingredients(self):
        """Test creating a recipe with new tags."""
        payload = {
            'title' : 'Grandmas Gumbo',
            'time_minutes': 60,
            'price' : Decimal('10.50'),
            'ingredients': [{'name': 'Sausage'}, {'name': 'Rice'}]
        }
        
        res = self.client.post(RECIPES_URL, payload, format='json')
        
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        self.assertEqual(recipe.ingredients.count(), 2) #make sure both ings get added
        for ing in payload['ingredients']: #makes sure the name gets added correctly & to the correct user
            exists = recipe.ingredients.filter(
                name=ing['name'],
                user=self.user
            ).exists()
            self.assertTrue(exists)
            
    def test_create_recipe_with_existing_ingedients(self):
        """Test creating a recipe with existing tag."""
        ingredient = Ingredient.objects.create(user=self.user, name='Cabbage')
        payload = {
            'title': 'Pho',
            'time_minutes': 60,
            'price' : Decimal('5.50'),
            'ingredients': [{'name': 'Cabbage'}, {'name': 'Siracha'}]
        }
        
        res = self.client.post(RECIPES_URL, payload, format='json')
        
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        self.assertEqual(recipe.ingredients.count(), 2) 
        self.assertIn(ingredient, recipe.ingredients.all())
        for ing in payload['ingredients']: #makes sure the name gets added correctly & to the correct user
            exists = recipe.ingredients.filter(
                name=ing['name'],
                user=self.user
            ).exists()
            self.assertTrue(exists)
            
            
    def test_create_ingredient_on_update(self):
        """test creating an ingredient when updating a recipe."""
        recipe = create_recipe(user=self.user)
        
        payload = {'ingredients': [{'name': 'Limes'}]}
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')
        
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        new_ing = Ingredient.objects.get(user=self.user, name='Limes')
        self.assertIn(new_ing, recipe.ingredients.all())
        
    def test_update_recipe_assign_ingredient(self):
        """Test assigning an existing ingredient when creating recipe."""
        ing = Ingredient.objects.create(user=self.user, name='Limes')
        recipe = create_recipe(user=self.user)
        recipe.ingredients.add(ing)
        
        ing2 = Ingredient.objects.create(user=self.user, name='Chili')
        payload = {'ingredients': [{'name': 'Chili'}]}
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')
        
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(ing2, recipe.ingredients.all())
        self.assertNotIn(ing, recipe.ingredients.all())
        
    def test_clear_recipe_ingredients(self):
        """Test clearing a recipes ingredients."""
        ing = Ingredient.objects.create(user=self.user, name='Chili')
        recipe = create_recipe(user=self.user)
        recipe.ingredients.add(ing)
        
        payload = {'ingredients': []}
        url = detail_url(recipe.id)
        res = self.client.patch(url, payload, format='json')
        
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.ingredients.count(), 0)
        
        
    def test_filter_by_tags(self):
        """Test filtering recipes by tags."""
        r1 = create_recipe(user=self.user, title='Cajun Gumbo')
        r2 = create_recipe(user=self.user, title='Poboys')
        
        tag1 = Tag.objects.create(user=self.user, name='Cajun')
        tag2 = Tag.objects.create(user=self.user,name='Southern')
        r1.tags.add(tag1)
        r2.tags.add(tag2)
        r3 = create_recipe(user=self.user, title='Catfish')
        
        params = {'tags': f"{tag1.id},{tag2.id}"}
        res = self.client.get(RECIPES_URL, params)
        
        s1 = RecipeSerializer(r1)
        s2 = RecipeSerializer(r2)
        s3 = RecipeSerializer(r3)
        
        self.assertIn(s1.data, res.data)
        self.assertIn(s2.data, res.data)
        self.assertNotIn(s3.data, res.data)
        
    def test_filter_by_ingredients(self):
        """Test filtering recipes by tags."""
        r1 = create_recipe(user=self.user, title='Cajun Gumbo')
        r2 = create_recipe(user=self.user, title='Poboys')
        
        ing1 = Ingredient.objects.create(user=self.user, name='Rice')
        ing2 = Ingredient.objects.create(user=self.user,name='Shrimp')
        r1.ingredients.add(ing1)
        r2.ingredients.add(ing2)
        r3 = create_recipe(user=self.user, title='Catfish')
        
        params = {'ingredients': f"{ing1.id},{ing2.id}"}
        res = self.client.get(RECIPES_URL, params)
        
        s1 = RecipeSerializer(r1)
        s2 = RecipeSerializer(r2)
        s3 = RecipeSerializer(r3)
        
        self.assertIn(s1.data, res.data)
        self.assertIn(s2.data, res.data)
        self.assertNotIn(s3.data, res.data)
        
        
class ImageUploadtests(TestCase):
    """Tests for the image upload API."""
    
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'user@example.com',
            'password123'
        )
        
        self.client.force_authenticate(self.user)
        self.recipe = create_recipe(user=self.user)
        
    def tearDown(self):
        self.recipe.image.delete()
        
    def test_upload_image(self):
        """Test uploading an image to a recipe."""
        url = image_upload_url(self.recipe.id)
        with tempfile.NamedTemporaryFile(suffix='.jpg') as image_file:
            img = Image.new('RGB', (10, 10)) #creates test image 10 x 10 pixels
            img.save(image_file, format='JPEG') #saving image to temporary file
            image_file.seek(0)
            payload = {'image': image_file}
            res = self.client.post(url, payload, format='multipart') #multipart form, best practice for uploading images
            
        self.recipe.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('image', res.data)
        self.assertTrue(os.path.exists(self.recipe.image.path))
        
    def test_upload_image_bad_request(self):
        """Test uploading invalid image."""
        url = image_upload_url(self.recipe.id)
        payload = {'image': 'notanimage.jpg'}
        res = self.client.post(url, payload, format='multipart')
        
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)