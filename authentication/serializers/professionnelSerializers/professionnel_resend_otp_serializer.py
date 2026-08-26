from rest_framework import serializers


class ProfessionnelResendOTPSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)