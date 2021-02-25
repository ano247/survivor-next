import json

from django.urls import reverse
from rest_framework.test import APITestCase

from user.models import Survivor, Advocate, CustomUser


class UserTestCase(APITestCase):
    survivor_attributes = {
        'username': 'some_survivor',
        'email': 'survivor@email.com',
        'password': 'some password',
        'user_token': '1',
        'device_token': 'ExponentPushToken[xxxxxxxxxxxxxxxxxxxxxx]'
    }

    advocate_attributes = {
        'username': 'some_advocate',
        'email': 'advocate@email.com',
        'password': 'some other password',
        'user_token': '2',
        'device_token': 'ExponentPushToken[yyyyyyyyyyyyyyyyyyyyyy]'
    }

    def create_user(self, attributes):
        user = CustomUser.objects.create_user(
            username=attributes['username'],
            email=attributes['email'],
            password=attributes['password'],
            user_token=attributes['user_token'],
            device_token=attributes['device_token']
        )

        return user

    def create_survivor(self, attributes=None):
        if not attributes:
            attributes = self.survivor_attributes

        user = self.create_user(attributes=attributes)

        return Survivor.objects.create(user=user).user.user_token

    def create_advocate(self, attributes=None):
        if not attributes:
            attributes = self.advocate_attributes

        user = self.create_user(attributes=attributes)

        return Advocate.objects.create(user=user).user.user_token

    def set_token(self, attributes):
        response = self.client.post(
            reverse('token-obtain-pair'),
            data=json.dumps({
                'username': attributes['username'],
                'password': attributes['password']
            }),
            content_type='application/json'
        )

        self.client.credentials(
            HTTP_AUTHORIZATION='Bearer ' + response.data['access']
        )
