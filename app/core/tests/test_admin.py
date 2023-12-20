"""
Tests for django admin modifications.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import Client 


class AdminSiteTests(TestCase):
    """Tests for Django admin."""
    
    def setUp(self):
        """Create user and client."""
        self.client = Client() #django test clients that allows us to make http requests
        self.admin_user = get_user_model().objects.create_superuser(
            'admin@example.com', 
            'testpass123'
            )
        self.client.force_login(self.admin_user)
        self.user = get_user_model().objects.create_user(
            'user@example.com', 
            'testpass123', 
            name='Test User'
            )
        
        
    def test_users_list(self):
        """Test that users are listed on page"""
        url = reverse('admin:core_user_changelist') #will display a page with list of users
        res = self.client.get(url) #get request to the above url to get the page
        
        self.assertContains(res, self.user.name) #check the response object to see if the page contains name & email
        self.assertContains(res, self.user.email)
        
    
    def test_edit_user_page(self):
        """Test the edit user page works."""
        url = reverse('admin:core_user_change', args=[self.user.id])
        res = self.client.get(url)
        
        self.assertEqual(res.status_code, 200)
        
        
    def test_create_user_page(self):
        """Test the create user page works."""
        url = reverse('admin:core_user_add')
        res = self.client.get(url)
        
        self.assertEqual(res.status_code, 200)