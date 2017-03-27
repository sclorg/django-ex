from rest_framework import serializers
from .models import UserResponse


class UserResponseSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    question = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = UserResponse
        fields = ('user', 'question', 'value')

    def create(self, validated_data):
        response = UserResponse(**validated_data)
        response.save()
        return response

    def update(self, instance, validated_data):
        instance.value = validated_data['value']
        instance.save()



