from django.db import models

from user.models import Advocate, Survivor

# can be any task


class Task(models.Model):
    survivor = models.ForeignKey(
        Survivor,
        on_delete=models.CASCADE,
    )

    advocate = models.ForeignKey(
        Advocate,
        on_delete=models.CASCADE,
        null=True,
    )

    details = models.CharField(max_length=264)

    status = models.CharField(
        max_length=16,
        default='pending',
    )

    deadline = models.DateField(
        null=True,
    )

    type = models.CharField(
        max_length=64,
        null=True,
    )
