from django.test import TestCase
from django.urls import reverse

class PaymentViewTests(TestCase):

    def test_payment_request_view(self):
        response = self.client.get(reverse('payment_request'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'client_key')

    def test_payment_success_view(self):
        response = self.client.get(reverse('payment_success'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Payment Successful')
