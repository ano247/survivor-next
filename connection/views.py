import time
from multiprocessing import Process

from rest_framework import status, permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from connection.models import Connection
from connection.serializers import ConnectionSerializer
from notification.exponent import send_push_message
from task.models import Task
from user.models import Advocate, Survivor


class UserIsSurvivor(permissions.BasePermission):
    def has_permission(self, request, view):
        return Survivor.objects.filter(user__user_token=request.user.user_token).exists()


class RequestConnectionView(APIView):
    permission_classes = (
        IsAuthenticated,
        UserIsSurvivor,
    )

    def post(self, request):
        connection = Connection.objects.create(
            survivor_id=request.user.user_token)

        process = Process(target=request_advocates(
            connection_id=connection.id, data=request.data))
        process.start()

        return Response(connection.id, status.HTTP_200_OK)


class UserIsAdvocate(permissions.BasePermission):
    def has_permission(self, request, view):
        return Advocate.objects.filter(user__user_token=request.user.user_token).exists()


class AcceptConnectionView(APIView):
    permission_classes = (
        IsAuthenticated,
        UserIsAdvocate,
    )

    def post(self, request):
        connection = Connection.objects.get(
            id=request.data.get('connection_id'))

        if connection.advocate_id:
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            survivor = Survivor.objects.get(
                user__user_token=connection.survivor_id)
            advocate = Advocate.objects.get(
                user__user_token=request.user.user_token)

            connection.advocate_id = advocate.user_id
            connection.save()

            message = f'Advocate {advocate.user.first_name} has accepted your request to connect'
            data = {
                'advocate_id': advocate.user_id,
                'advocate_name': advocate.user.first_name
            }

            send_push_message(
                survivor.user.device_token,
                message=message,
                notification_type='connection-accepted',
                data=data
            )

            if 'task_id' in request.data:
                task = Task.objects.get(id=request.data.get('task_id'))
                task.advocate_id = request.user.user_token
                task.save()

            return Response(status=status.HTTP_200_OK)


class ListConnections(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = request.user

        if hasattr(user, 'survivor'):
            result = Connection.objects.filter(
                survivor_id=user.user_token).exclude(advocate_id__isnull=True)
        else:
            result = Connection.objects.filter(advocate_id=user.user_token)

        return Response(ConnectionSerializer(result, many=True).data, status=status.HTTP_200_OK)


def request_advocates(connection_id, data):
    sleep_time = 30  # 30 sec timer

    survivor_id = Connection.objects.get(id=connection_id).survivor_id
    survivor = Survivor.objects.get(user__user_token=survivor_id)

    case_type = data.get('case_type', 'police')

    advocates = Advocate.objects.filter(type=case_type)

    for advocate in advocates:
        connection = Connection.objects.get(id=connection_id)

        if connection.advocate_id:
            break

        message = f'{survivor.user.first_name} has requested to connect with you'
        data = {
            'survivor_id': survivor_id,
            'connection_id': connection_id,
            'survivor_name': survivor.user.first_name,
            **data
        }

        send_push_message(
            advocate.user.device_token,
            message=message,
            notification_type='connection-requested',
            data=data
        )

        time.sleep(sleep_time)
