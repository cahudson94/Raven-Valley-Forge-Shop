"""Test file for account views, models, urls, and forms."""
from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client
from django.urls import reverse_lazy
from account.models import Account, ShippingInfo
from catalog.models import Product, Service
import os


test_image = SimpleUploadedFile(name='pic.jpg',
                                content=open(os.path.join(settings.BASE_DIR,
                                                          'static/isis.jpg'),
                                             'rb').read(),
                                content_type='image/jpeg')


class BasicViewTests(TestCase):
    """Tests for basic gets on views."""

    def setUp(self):
        """Setup."""
        self.client = Client()
        self.user = User(username='cookiemonster',
                         email='cookie@cookie.cookie')
        self.user.set_password('COOKIE')
        self.user.is_active = True
        self.user.save()
        self.account = Account.objects.get(user=self.user)
        self.account.has_address_delete = True
        self.account.save()
        self.addresses = []
        self.products = []
        self.services = []
        for i in range(2):
            address = ShippingInfo(name='test_name',
                                   address1='1234 Test Ave S',
                                   zip_code='11111',
                                   city='testville',
                                   state='testington',
                                   resident=self.account)
            address.save()
            product = Product(image=test_image,
                              name=('test' + str(i)),
                              price=50.00)
            product.save()
            service = Service(image=test_image,
                              name=('test' + str(i)))
            service.save()
            self.addresses.append(address)
            self.products.append(product)
            self.services.append(service)
        self.account.main_address = ShippingInfo.objects.last().id
        self.account.save()

    def test_account_200(self):
        """Test 200 response from account view."""
        self.client.force_login(self.user)
        response = self.client.get(reverse_lazy('account'))
        self.assertEqual(200, response.status_code)

    def test_add_address_200(self):
        """Test 200 response from add address view."""
        self.client.force_login(self.user)
        response = self.client.get(reverse_lazy('add_add'))
        self.assertEqual(200, response.status_code)

    def test_address_list_200(self):
        """Test 200 response from address list view."""
        self.client.force_login(self.user)
        response = self.client.get(reverse_lazy('add_list'))
        self.assertEqual(200, response.status_code)

    def test_del_address_200(self):
        """Test 200 response from delete address view."""
        self.client.force_login(self.user)
        response = self.client.get(reverse_lazy('del_add',
                                   kwargs={'pk': ShippingInfo.objects.last().id}))
        self.assertEqual(200, response.status_code)

    def test_edit_account_200(self):
        """Test 200 response from edit account view."""
        self.client.force_login(self.user)
        response = self.client.get(reverse_lazy('edit_acc',
                                   kwargs={'pk': Account.objects.last().id}))
        self.assertEqual(200, response.status_code)

    def test_info_form_not_complete_200(self):
        """Test 200 response from info form view if not complete."""
        self.client.force_login(self.user)
        response = self.client.get(reverse_lazy('info_reg',
                                   kwargs={'pk': Account.objects.last().id}))
        self.assertEqual(200, response.status_code)

    def test_about_view_with_accounts(self):
        """Test when staff have accounts."""
        matt = User(username='m.ravenmoore')
        matt.save()
        matt.account.pic = test_image
        matt.account.save()
        becky = User(username='b.ravenmoore')
        becky.save()
        becky.account.pic = test_image
        becky.account.save()
        gordon = User(username='gordon')
        gordon.save()
        gordon.account.pic = test_image
        gordon.account.save()
        response = self.client.get(reverse_lazy('about'))
        pic_count = response.content.decode().count('/media/profile_pics/pic')
        self.assertEqual(pic_count, 3)

    def test_account_view_cart(self):
        """Test that cart content is in html when items in cart."""
        self.client.force_login(self.user)
        response = self.client.get(reverse_lazy('account'))
        self.assertIn('Your cart is empty.', response.content.decode())
        self.assertEqual('', self.account.cart)
        self.client.post(reverse_lazy('prod',
                                      kwargs={'pk': Product.objects.last().id}),
                         {'add': ''})
        response = self.client.get(reverse_lazy('account'))
        self.account = Account.objects.get(user=self.user)
        self.assertFalse('' == self.account.cart)
        self.assertIn('test', response.content.decode())

    def test_account_view_saved_products(self):
        """Test that saved products are in html."""
        self.client.force_login(self.user)
        response = self.client.get(reverse_lazy('account'))
        self.assertIn('You have no saved products yet.', response.content.decode())
        self.assertEqual('', self.account.saved_products)
        self.client.post(reverse_lazy('prod',
                                      kwargs={'pk': Product.objects.last().id}))
        response = self.client.get(reverse_lazy('account'))
        self.account = Account.objects.get(user=self.user)
        self.assertFalse('' == self.account.saved_products)
        self.assertIn('test', response.content.decode())

    def test_account_view_saved_services(self):
        """Test that saved services are in html."""
        self.client.force_login(self.user)
        response = self.client.get(reverse_lazy('account'))
        self.assertIn('You have no saved services yet.', response.content.decode())
        self.assertEqual('', self.account.saved_services)
        self.client.post(reverse_lazy('serv',
                                      kwargs={'pk': Service.objects.last().id}))
        response = self.client.get(reverse_lazy('account'))
        self.account = Account.objects.get(user=self.user)
        self.assertFalse('' == self.account.saved_services)
        self.assertIn('test', response.content.decode())

    def test_account_view_product_history(self):
        """Test that purchase history is in html."""
        self.client.force_login(self.user)
        response = self.client.get(reverse_lazy('account'))
        self.assertIn('You have not purchased any products yet.', response.content.decode())
        self.account.purchase_history = '{"item_id": %s, "type": "prod"}' % Product.objects.last().id
        self.account.save()
        response = self.client.get(reverse_lazy('account'))
        self.assertFalse('' == self.account.purchase_history)
        self.assertIn('test', response.content.decode())

    def test_account_view_service_history(self):
        """Test that service history is in html."""
        self.client.force_login(self.user)
        response = self.client.get(reverse_lazy('account'))
        self.assertIn('You have not purchased any services yet.', response.content.decode())
        self.account.service_history = '{"item_id": %s, "type": "serv"}' % Service.objects.last().id
        self.account.save()
        response = self.client.get(reverse_lazy('account'))
        self.assertFalse('' == self.account.service_history)
        self.assertIn('test', response.content.decode())

    def test_add_address_succes(self):
        """Test adding an address successfully."""
        self.client.force_login(self.user)
        self.assertEqual(2, len(self.account.shippinginfo_set.values()))
        self.client.post(reverse_lazy('add_add'),
                         {'name': 'Chris',
                          'address1': 'Jamaica',
                          'zip_code': '98178',
                          'city': 'Seattle',
                          'main': False,
                          'state': 'Alabama',
                          'address2': 'man'})
        self.assertEqual(3, len(self.account.shippinginfo_set.values()))
        self.assertEqual('Chris', self.account.shippinginfo_set.values()[0]['name'])

    def test_add_address_main(self):
        """Test adding an address successfully."""
        self.client.force_login(self.user)
        self.assertEqual(2, len(self.account.shippinginfo_set.values()))
        self.client.post(reverse_lazy('add_add'),
                         {'name': 'Chris',
                          'address1': 'Jamaica',
                          'zip_code': '98178',
                          'city': 'Seattle',
                          'main': True,
                          'state': 'Alabama',
                          'address2': 'man'})
        self.assertEqual(3, len(self.account.shippinginfo_set.values()))
        new_add_id = ShippingInfo.objects.last().id
        self.account = Account.objects.get(user=self.user)
        self.assertEqual(new_add_id, self.account.main_address)

    def test_change_main_address(self):
        """Test changing which address is main."""
        self.client.force_login(self.user)
        add_id = str(ShippingInfo.objects.last().id)
        pass
