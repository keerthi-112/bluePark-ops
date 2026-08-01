from django.contrib.auth.models import User
from rest_framework import serializers

from core.constants import ROLE_CHOICES, ROLE_CUSTOMER


class MeSerializer(serializers.ModelSerializer):
    role = serializers.CharField(source='profile.role', read_only=True)
    phone = serializers.CharField(source='profile.phone', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'phone']


STAFF_ROLE_CHOICES = [choice for choice in ROLE_CHOICES if choice[0] != ROLE_CUSTOMER]


class CreateStaffSerializer(serializers.Serializer):
    """Used by a Manager/Admin to create a Waiter/Chef/Manager/Admin account.
    Customers create their own accounts through accounts.views.register."""

    username = serializers.CharField(max_length=150)
    email = serializers.EmailField(required=False, allow_blank=True, default='')
    password = serializers.CharField(write_only=True, min_length=8)
    role = serializers.ChoiceField(choices=STAFF_ROLE_CHOICES)

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError('That username is already taken.')
        return value

    def create(self, validated_data):
        role = validated_data.pop('role')
        user = User.objects.create_user(**validated_data)
        user.profile.role = role
        user.profile.save(update_fields=['role'])
        return user
