from rest_framework import serializers

from user.models import CustomUser, Survivor, Advocate


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = '__all__'

    def create(self, validated_data):
        user = super(CustomUserSerializer, self).create(validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user

    def update(self, instance, validated_data):
        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        if 'password' in validated_data:
            instance.set_password(validated_data.get('password'))
        instance.user_token = validated_data.get('user_token', instance.user_token)
        instance.device_token = validated_data.get('device_token', instance.device_token)

        instance.save()

        return instance

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation.pop('password')
        return representation


class SurvivorSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer()

    class Meta:
        model = Survivor
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation.update(representation.pop('user'))
        return representation


class AdvocateSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer()

    class Meta:
        model = Advocate
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation.update(representation.pop('user'))
        return representation
