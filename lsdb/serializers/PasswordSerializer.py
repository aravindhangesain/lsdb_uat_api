from rest_framework import serializers

class LostPasswordSerializer(serializers.Serializer):
    """
    Serializer for lost password endpoint.
    """
    new_password = serializers.CharField(required=True)

class PasswordSerializer(serializers.Serializer):
    """
    Serializer for password change endpoint.
    """
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

class InviteUserSerializer(serializers.Serializer):
    username = serializers.CharField(required = True)

class ForgotPasswordSerializer(serializers.Serializer):
    username = serializers.CharField(required = True)
