from rest_framework import serializers

from connection.models import Connection
from user.models import Survivor, Advocate


class ConnectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Connection
        fields = ('survivor', 'advocate')

    def to_representation(self, instance):
        survivor = Survivor.objects.get(user__user_token=instance.survivor_id)
        advocate = Advocate.objects.get(user__user_token=instance.advocate_id)

        representation = super().to_representation(instance)
        representation.update({
            'survivor_name': survivor.user.first_name,
            'advocate_name': advocate.user.first_name,
            'case_type': advocate.type
        })
        return representation
