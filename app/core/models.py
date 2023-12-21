"""
Database models.
"""

from django.db import models
from django.conf import settings 
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin
)

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
        return str(self.name)