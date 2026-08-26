from rest_framework import serializers


class ProfessionnelCheckEmailSerializer(serializers.Serializer):

    email = serializers.EmailField(
        required=True
    )