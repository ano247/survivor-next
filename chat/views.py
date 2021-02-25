from rest_framework import permissions, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from chat.models import Chat
from chat.serializers import ChatSerializer
from connection.models import Connection
from notification.exponent import send_push_message


class UserIsConnected(permissions.BasePermission):
    def has_permission(self, request, view):
        sender = request.user
        receiver_id = request.data.get('receiver')

        survivor_id = sender.user_token if hasattr(sender, 'survivor') else receiver_id
        advocate_id = sender.user_token if hasattr(sender, 'advocate') else receiver_id

        return Connection.objects.filter(survivor_id=survivor_id, advocate_id=advocate_id).exists()


class SendMessageView(APIView):
    permission_classes = (
        IsAuthenticated,
        UserIsConnected
    )

    def post(self, request):
        data = {**request.data, **{'sender': request.user.user_token}}
        serializer = ChatSerializer(data=data)

        if serializer.is_valid():
            chat = serializer.save()
            message = chat.sender.username + ': ' + chat.message
            send_push_message(
                token=chat.receiver.device_token,
                message=message,
                notification_type='message-received',
                data=ChatSerializer(chat).data
            )
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class ChatHistoryView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, user_id):
        this = request.user.user_token
        that = user_id

        sent = Chat.objects.filter(sender_id=this, receiver_id=that).order_by('time')
        received = Chat.objects.filter(sender_id=that, receiver_id=this).order_by('time')

        return Response(ChatSerializer(sent | received, many=True).data, status=status.HTTP_200_OK)
