"""Test file for base html and main url/views."""
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
        self.user.is_superuser = True
        self.user.is_active = True
        self.user.is_staff = True
        self.user.save()

    def test_home_ok(self):
        """Test that home page is available to logged out user."""
        resp = self.client.get(reverse_lazy('home'))
        self.assertEqual(resp.status_code, 200)

    def test_home_page_no_logout_when_not_logged_in(self):
        """Test logout not on homepage."""
        response = self.client.get(reverse_lazy('home'))
        self.assertTrue('Login' in response.content.decode())
        self.assertFalse('Logout' in response.content.decode())

    def test_no_reg_button_when_logged_in(self):
        """Registration button dissapears on login."""
        self.client.force_login(self.user)
        response = self.client.get(reverse_lazy('home'))
        self.assertTrue('Logout' in response.content.decode())
        self.assertFalse('Login' in response.content.decode())
