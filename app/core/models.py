"""
Database models.
"""

import uuid
import os

from django.db import models
from django.conf import settings 
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin
)

def recipe_image_file_path(instance, filename):
    """Generate file path for new recipe image."""
    ext = os.path.splitext(filename)[1] #splits the filname and grabs the extension
    filename = f"{uuid.uuid4()}{ext}" #create new file name with the uuid & original extension
    
    return os.path.join('uploads', 'recipe', filename) #using os.path to make sure the 
                                                       #string is correct format no matter the operating system

class UserManager(BaseUserManager):
    """Manager for users."""
    
    def create_user(self, email, password=None, **extra_fields):
        """Create, save and return a new user."""
        if not email:
            raise ValueError('User must have an email address')
        user = self.model(email=self.normalize_email(email),**extra_fields) #normalize_email method comes from BaseUserManager
        user.set_password(password) #django default hashing mechanism
        user.save(using=self._db) #allows the object to be saved to multiple dbs if we have multiple
        
        return user 
    
    def create_superuser(self, email, password=None, **extra_fields):
        """Create and return a new superuser."""
        
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True 
        user.save(using=self._db)
        
        return user 

class User(AbstractBaseUser, PermissionsMixin):
    """User object in the database."""
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    
    objects = UserManager() #calls upon the UserManager class to create a new user object
    
    
    USERNAME_FIELD = 'email'
    
    
class Recipe(models.Model):
    """Recipe object in the database."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    time_minutes = models.IntegerField()
    price = models.DecimalField(max_digits=5, decimal_places=2)
    link = models.CharField(max_length=255, blank=True)
    tags = models.ManyToManyField('Tag')
    ingredients = models.ManyToManyField('Ingredient')
    image = models.ImageField(null=True, upload_to=recipe_image_file_path) #allows you to specify a function to generate the endpoint/path name
    
    def __str__(self):
        return self.title
    
    
class Tag(models.Model):
    """Tag for filtering recipes."""
    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    
    
    def __str__(self):
        return self.name

class Ingredient(models.Model):
    """Ingredients for recipes."""
    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    
    
    def __str__(self):
        return self.name