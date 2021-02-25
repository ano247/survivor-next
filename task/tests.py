import json

from django.urls import reverse
from rest_framework import status

from connection.models import Connection
from task.models import Task
from utility.test import UserTestCase


class TaskTest(UserTestCase):
    def setUp(self):
        self.survivor_id = self.create_survivor()
        self.advocate_id = self.create_advocate()

        self.connection_id = Connection.objects.create(survivor_id=self.survivor_id, advocate_id=self.advocate_id).id

        self.set_token(self.advocate_attributes)
        self.url = reverse('task:task', args=(self.survivor_id,))

    def test_post(self):
        details = 'test'

        response = self.client.post(
            self.url,
            data=json.dumps({'details': details}),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        task = response.data

        self.assertTrue('id' in task)
        self.assertEqual(task['survivor'], self.survivor_id)
        self.assertEqual(task['advocate'], self.advocate_id)
        self.assertEqual(task['details'], details)
        self.assertEqual(task['status'], 'pending')

    def test_unauthorized(self):
        advocate_attributes = {
            'username': 'some other advocate',
            'email': 'other_advocate@email.com',
            'password': 'some other password',
            'user_token': '3',
            'device_token': 'ExponentPushToken[zzzzzzzzzzzzzzzzzzzzzz]'
        }

        self.create_advocate(advocate_attributes)
        self.set_token(advocate_attributes)

        response = self.client.post(
            self.url,
            data=json.dumps({'details': 'details'}),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_get(self):
        self.client.post(
            self.url,
            data=json.dumps({'details': 'test'}),
            content_type='application/json'
        )

        response = self.client.get(
            self.url,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_put(self):
        response = self.client.post(
            self.url,
            data=json.dumps({'details': 'test'}),
            content_type='application/json'
        )

        task_id = response.data['id']

        response = self.client.put(
            self.url,
            data=json.dumps({
                'task_id': task_id,
                'status': 'completed',
            }),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        task = Task.objects.get(id=task_id)
        self.assertEqual(task.status, 'completed')
