"""Test file for base html, main url/views, and google api calls."""
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse_lazy


class BaseHtmlTests(TestCase):
    """Tests for various responsive rapping content."""

    def setUp(self):
        """Setup."""
        self.client = Client()
        self.user = User(username='cookiemonster',
                         email='cookie@cookie.cookie')
        self.user.set_password('COOKIE')
        self.user.is_active = True
        self.user.save()

    def test_home_ok(self):
        """Test that home page is available to logged out user."""
        resp = self.client.get(reverse_lazy('home'))
        self.assertEqual(resp.status_code, 200)

    def test_login_when_not_logged(self):
        """Test logout not on homepage."""
        response = self.client.get(reverse_lazy('home'))
        self.assertTrue('Login' in response.content.decode())
        self.assertTrue('Register' in response.content.decode())
        self.assertFalse('Logout' in response.content.decode())

    def test_logout_reg_buttons_when_logged_in(self):
        """Registration and login buttons dissapears on login."""
        self.client.force_login(self.user)
        response = self.client.get(reverse_lazy('home'))
        self.assertTrue('Logout' in response.content.decode())
        self.assertFalse('Login' in response.content.decode())
        self.assertFalse('Register' in response.content.decode())

    def test_staff_buttons_when_logged_in(self):
        """Registration button dissapears on login."""
        self.client.force_login(self.user)
        response = self.client.get(reverse_lazy('home'))
        self.assertTrue('Logout' in response.content.decode())
        self.assertFalse('Login' in response.content.decode())
        self.assertFalse('Orders' in response.content.decode())
        self.assertFalse('Items' in response.content.decode())
        self.assertFalse('Users' in response.content.decode())
        self.user.is_staff = True
        self.user.save()
        self.client.force_login(self.user)
        response = self.client.get(reverse_lazy('home'))
        self.assertTrue('Orders' in response.content.decode())
        self.assertTrue('Items' in response.content.decode())
        self.assertTrue('Users' in response.content.decode())

    def test_admin_button_when_superuser(self):
        """Admin button present for superusers only."""
        self.client.force_login(self.user)
        response = self.client.get(reverse_lazy('home'))
        self.assertFalse('Admin' in response.content.decode())
        self.user.is_staff = True
        self.user.is_superuser = True
        self.user.save()
        self.client.force_login(self.user)
        response = self.client.get(reverse_lazy('home'))
        self.assertTrue('Admin' in response.content.decode())

    def test_home_200(self):
        """Test 200 response from home view."""
        response = self.client.get(reverse_lazy('home'))
        self.assertEqual(200, response.status_code)

    def test_about_200(self):
        """Test 200 response from about view."""
        response = self.client.get(reverse_lazy('about'))
        self.assertEqual(200, response.status_code)

    def test_contact_200(self):
        """Test 200 response from contact view."""
        response = self.client.get(reverse_lazy('contact'))
        self.assertEqual(200, response.status_code)

    def test_users_200(self):
        """Test 200 response from users view."""
        response = self.client.get(reverse_lazy('users'))
        self.assertEqual(200, response.status_code)

    def test_orders_200(self):
        """Test 200 response from orders view."""
        response = self.client.get(reverse_lazy('orders'))
        self.assertEqual(200, response.status_code)

    def test_login_200(self):
        """Test 200 response from login view."""
        response = self.client.get(reverse_lazy('login'))
        self.assertEqual(200, response.status_code)

    def test_register_200(self):
        """Test 200 response from register view."""
        response = self.client.get(reverse_lazy('register'))
        self.assertEqual(200, response.status_code)
