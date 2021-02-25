import json

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from parameterized import parameterized
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.test import APITestCase

from user.views import get_user

User = get_user_model()


class UsersManagersTests(TestCase):
    username = 'some_username'
    email = 'some@email.com'
    password = 'some password'
    user_token = 'some user_token'
    device_token = 'some device_token'

    def test_create_user(self):
        user = User.objects.create_user(
            username=self.username,
            email=self.email,
            password=self.password,
            user_token=self.user_token,
            device_token=self.device_token
        )

        self.assertEqual(user.username, self.username)
        self.assertEqual(user.email, self.email)
        self.assertEqual(user.user_token, self.user_token)
        self.assertEqual(user.device_token, self.device_token)
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)


class UserTestCase(APITestCase):
    create_attributes = {
        'username': 'some_username',
        'email': 'some@email.com',
        'password': 'some password',
        'user_token': 'some user_token',
        'device_token': 'some device_token',
    }

    update_attributes = {
        'username': 'some_updated_username',
        'email': 'some_updated@email.com',
        'password': 'some updated password',
        'user_token': 'some user_token',
        'device_token': 'some updated device_token',
    }

    def assertEqualAttributes(self, actual, expected):
        self.assertEqual(actual.username, expected['username'])
        self.assertEqual(actual.email, expected['email'])
        self.assertTrue(actual.check_password(expected['password']))
        self.assertEqual(actual.device_token, expected['device_token'])


class RegisterUserTest(UserTestCase):
    @parameterized.expand([('survivor',), ('advocate',)])
    def test_user(self, user_type):
        response = self.client.post(
            reverse(f'user:{user_type}-register'),
            data=json.dumps(self.create_attributes),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertTrue('user_token' in response.data)

        user = User.objects.get(user_token=response.data['user_token'])
        self.assertEqualAttributes(user, self.create_attributes)

    def test_advocate(self):
        response = self.client.post(
            reverse('user:advocate-register'),
            data=json.dumps({
                **self.create_attributes,
                'type': 'some type',
            }),
            content_type='application/json'
        )

        self.assertEqual(response.data['type'], 'some type')

    @parameterized.expand([('survivor',), ('advocate',)])
    def test_invalid_data(self, user_type):
        response = self.client.post(
            reverse(f'user:{user_type}-register'),
            data=json.dumps({}),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserInformationTest(UserTestCase):
    def setUp(self):
        self.user_token = self.create_user(self.create_attributes)
        self.url = reverse('user:user-information', args=(self.user_token,))
        self.set_token(self.create_attributes)

    def test_user_from_id_absent(self):
        self.assertRaises(NotFound, lambda: get_user(0))

    def test_get(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        user_token = response.data['user_token']
        self.assertEqual(user_token, self.user_token)

        user = User.objects.get(user_token=user_token)
        self.assertEqualAttributes(user, self.create_attributes)

    def test_put(self):
        response = self.client.put(
            self.url,
            data=json.dumps(self.update_attributes),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        user_token = response.data['user_token']
        self.assertEqual(user_token, self.user_token)

        user = User.objects.get(user_token=user_token)
        self.assertEqualAttributes(user, self.update_attributes)

    def test_delete(self):
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(User.objects.get(user_token=self.user_token).is_active)

        response = self.client.post(
            reverse('token-obtain-pair'),
            data=json.dumps({
                'username': self.create_attributes['username'],
                'password': self.create_attributes['password']
            }),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthorized(self):
        self.create_user(self.update_attributes)
        self.set_token(self.update_attributes)

        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def create_user(self, attributes):
        response = self.client.post(
            reverse('user:survivor-register'),
            data=json.dumps(attributes),
            content_type='application/json'
        )

        return response.data['user_token']

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
