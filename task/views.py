from rest_framework import status, permissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from connection.models import Connection
from notification.exponent import send_push_message
from task.models import Task
from task.serializers import TaskSerializer
from user.models import Survivor


class UserIsOwnerOrAdvocate(permissions.BasePermission):
    def has_permission(self, request, view):
        survivor_id = view.kwargs['survivor_id']

        return request.user.user_token == survivor_id or Connection.objects.filter(
            survivor_id=survivor_id,
            advocate_id=request.user.user_token
        ).exists()


class TaskView(APIView):
    permission_classes = (
        IsAuthenticated,
        UserIsOwnerOrAdvocate,
    )

    def post(self, request, survivor_id):
        request.data['survivor'] = survivor_id
        request.data['advocate'] = request.user.user_token

        serializer = TaskSerializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            task = serializer.save()
            send_push_message(
                token=Survivor.objects.get(user__user_token=survivor_id).user.device_token,
                message='task',
                notification_type='task-assigned',
                data={'details': task.details}
            )
            return Response(TaskSerializer(task).data, status=status.HTTP_201_CREATED)

    def get(self, request, survivor_id):
        result = Task.objects.filter(survivor_id=survivor_id)
        return Response(TaskSerializer(result, many=True).data, status=status.HTTP_200_OK)

    def put(self, request, survivor_id):
        task = Task.objects.get(id=request.data.get('task_id'))

        task.status = request.data.get('status', task.status)
        task.type = request.data.get('type', task.type)
        task.deadline = request.data.get('deadline', task.deadline)

        task.save()

        return Response(TaskSerializer(task).data, status=status.HTTP_200_OK)
