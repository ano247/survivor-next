import json

from django.urls import reverse
from rest_framework import status

from connection.models import Connection
from utility.test import UserTestCase


class ChatTest(UserTestCase):
    def setUp(self):
        self.survivor_id = self.create_survivor()
        self.advocate_id = self.create_advocate()

        self.connection_id = Connection.objects.create(
            survivor_id=self.survivor_id,
            advocate_id=self.advocate_id
        ).id

    def test_send(self):
        self.set_token(self.survivor_attributes)

        response = self.client.post(
            reverse('chat:message-send'),
            data=json.dumps({
                'receiver': self.advocate_id,
                'message': 'message'
            }),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_unauthorized(self):
        Connection.objects.get(id=self.connection_id).delete()

        self.set_token(self.survivor_attributes)

        response = self.client.post(
            reverse('chat:message-send'),
            data=json.dumps({
                'receiver': self.advocate_id,
                'message': 'message'
            }),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_history_sender(self):
        self.set_token(self.survivor_attributes)

        message = 'test'
        self.send_message(self.advocate_id, message)

        response = self.client.get(
            reverse('chat:chat-history', args=(self.advocate_id,))
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqualMessage(response, message)

    def test_history_receiver(self):
        self.set_token(self.survivor_attributes)

        message = 'test'
        self.send_message(self.advocate_id, message)

        self.set_token(self.advocate_attributes)

        response = self.client.get(
            reverse('chat:chat-history', args=(self.survivor_id,))
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqualMessage(response, message)

    def test_sequence(self):
        self.set_token(self.survivor_attributes)
        self.send_message(self.advocate_id)

        self.set_token(self.advocate_attributes)
        for _ in range(2):
            self.send_message(self.survivor_id)

        self.set_token(self.survivor_attributes)
        self.send_message(self.advocate_id)

        response = self.client.get(
            reverse('chat:chat-history', args=(self.advocate_id,))
        )

        last = ''
        for message in response.data:
            time = dict(message)['time']
            self.assertTrue(time > last)
            last = time

    def send_message(self, receiver_id, message='test'):
        self.client.post(
            reverse('chat:message-send'),
            data=json.dumps({
                'receiver': receiver_id,
                'message': message
            }),
            content_type='application/json'
        )

    def assertEqualMessage(self, response, message):
        history = dict(next(iter(response.data)))
        self.assertEqual(history['sender'], self.survivor_id)
        self.assertEqual(history['receiver'], self.advocate_id)
        self.assertEqual(history['message'], message)
