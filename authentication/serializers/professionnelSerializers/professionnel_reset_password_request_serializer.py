from rest_framework import serializers
from adminToorrii.models import Professionnel

class ProfessionnelResetPasswordRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not Professionnel.objects.filter(email=value).exists():
            raise serializers.ValidationError("Aucun compte professionnel avec cet email.")
        return value