from django.contrib.auth import authenticate
from rest_framework import serializers

from mainapp.models import User
from .validators import validate_username


class LoginSerializer(serializers.Serializer):
    phone = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):

        user = authenticate(username=attrs['phone'], password=attrs['password'])

        if not user:
            raise serializers.ValidationError('Incorrect phone or password.')

        if not user.is_active:
            raise serializers.ValidationError('User is disabled.')

        return {'user': user}


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id',
            'phone',
            'password',
            'is_active',
            'last_login',
            'joined_at',
        )
        read_only_fields = ('last_login', 'is_active', 'joined_at')
        extra_kwargs = {
            'password': {'required': True, 'write_only': True},
            'phone': {'required': True}
        }

    @staticmethod
    def validate_email(value):
        return validate_username(value)

    def create(self, validated_data):
        return User.objects.create_user(
            validated_data.pop('phone'),
            validated_data.pop('password'),
            **validated_data
        )
