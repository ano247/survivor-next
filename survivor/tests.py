import json

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class GenerateTokenTest(APITestCase):
    create_attributes = {
        'username': 'some_username',
        'email': 'some@email.com',
        'password': 'some password',
        'user_token': 'some user_token'
    }

    url = reverse('token-obtain-pair')

    def setUp(self):
        response = self.client.post(
            reverse('user:survivor-register'),
            data=json.dumps(self.create_attributes),
            content_type='application/json'
        )

        self.user_token = response.data['user_token']

    def test_device_token(self):
        response = self.client.post(
            self.url,
            json.dumps(self.create_attributes),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
