from rest_framework import serializers


class ProfessionnelVerifyOTPSerializer(serializers.Serializer):

    email = serializers.EmailField(required=True)

    code_verification = serializers.CharField(
        max_length=6,
        required=True
    )