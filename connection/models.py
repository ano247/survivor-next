from django.db import models

from user.models import Advocate, Survivor


class Connection(models.Model):
    survivor = models.ForeignKey(
        Survivor,
        on_delete=models.CASCADE,
    )

    advocate = models.ForeignKey(
        Advocate,
        on_delete=models.CASCADE,
        null=True,
    )
