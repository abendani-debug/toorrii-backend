from rest_framework import serializers
from adminToorrii.models import Professionnel

class ProfessionnelResetPasswordVerifySerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)
    new_password = serializers.CharField(min_length=6)

    def validate(self, data):
        try:
            user = Professionnel.objects.get(email=data['email'])
        except Professionnel.DoesNotExist:
            raise serializers.ValidationError("Compte introuvable.")

        if user.code_verification_reset_password != data['otp']:
            raise serializers.ValidationError("Code OTP incorrect.")

        return data