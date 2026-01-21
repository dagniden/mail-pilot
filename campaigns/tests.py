from django.test import TestCase
from django.contrib.auth import get_user_model
from campaigns.models import Campaign, CampaignAttempt, MessageTemplate, Client

User = get_user_model()


class ClientModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='test@example.com',
            email='test@example.com',
            password='testpass123'
        )
        self.client_obj = Client.objects.create(
            email='client@example.com',
            full_name='Test Client',
            owner=self.user
        )

    def test_get_absolute_url(self):
        expected_url = f'/campaigns/clients/{self.client_obj.pk}/'
        self.assertEqual(self.client_obj.get_absolute_url(), expected_url)

    def test_str_method(self):
        self.assertEqual(str(self.client_obj), 'Test Client <client@example.com>')