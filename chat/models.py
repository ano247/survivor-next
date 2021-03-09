from django.db import models
from django.utils.timezone import now

from user.models import CustomUser
# FK


class Chat(models.Model):
    sender = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='sender',
    )

    receiver = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='receiver',
    )

    message = models.CharField(max_length=1024)

    time = models.DateTimeField(default=now)
