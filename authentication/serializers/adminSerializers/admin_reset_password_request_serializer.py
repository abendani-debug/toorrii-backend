from rest_framework import serializers
from adminToorrii.models import AdminUser

class AdminResetPasswordRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not AdminUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("Aucun compte administrateur avec cet email.")
        return value