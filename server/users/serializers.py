from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import UserRole

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the custom user model
    """
    class Meta:
        model = User
        fields = ('id', 'email', 'name', 'phone_number', 'role', 'is_verified', 'date_joined')
        read_only_fields = ('id', 'is_verified', 'date_joined')


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration
    """
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('email', 'name', 'phone_number', 'role', 'password', 'password2')
        extra_kwargs = {
            'name': {'required': True},
            'phone_number': {'required': True},
            'role': {'required': True}
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        
        # Validate role
        if attrs['role'] not in [choice[0] for choice in UserRole.choices]:
            raise serializers.ValidationError({"role": "Invalid role selected."})
        
        # Admin role can only be set by superusers
        if attrs['role'] == UserRole.ADMIN:
            user = self.context.get('request').user
            if not user or not user.is_superuser:
                raise serializers.ValidationError({"role": "You cannot set admin role."})
        
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        return user


class PasswordChangeSerializer(serializers.Serializer):
    """
    Serializer for password change
    """
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    new_password2 = serializers.CharField(required=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError({"new_password": "Password fields didn't match."})
        return attrs


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating user profile
    """
    class Meta:
        model = User
        fields = ('name', 'phone_number')
        extra_kwargs = {
            'name': {'required': True},
            'phone_number': {'required': True}
        }


class AdminUserUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for admin to update user details including role
    """
    class Meta:
        model = User
        fields = ('name', 'phone_number', 'role', 'is_verified', 'is_active')
