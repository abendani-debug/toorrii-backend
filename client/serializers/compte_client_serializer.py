import re
from rest_framework import serializers
from phonenumber_field.serializerfields import PhoneNumberField
from datetime import datetime

class DemandeProfileClientSerializer(serializers.Serializer):
    
    numero_telephone = PhoneNumberField(
        region='DZ',
        help_text="Numéro de téléphone du client (doit commencer par +213)"
    )

    code_ticket = serializers.CharField(
        help_text="Code du ticket (ex: CTK-20260427-0001)"
    )

    #  Validation du numéro (forcer +213)
    def validate_numero_telephone(self, value):
        if not str(value).startswith("+213"):
            raise serializers.ValidationError(
                "Le numéro de téléphone doit être au format algérien (+213)"
            )
        return value

    

    def validate_code_ticket(self, value):
        pattern = r"^CTK-(\d{8})-(\d{4})$"
        match = re.match(pattern, value)

        if not match:
            raise serializers.ValidationError(
                "Format invalide. Exemple : CTK-20260427-0001"
            )

        date_part = match.group(1)

        try:
            datetime.strptime(date_part, "%Y%m%d")
        except ValueError:
            raise serializers.ValidationError("Date invalide dans le code ticket")

        return value


class AfficherProfileClientSerializer(serializers.Serializer):
    nom = serializers.CharField(allow_null=True)
    prenom = serializers.CharField(allow_null=True)
    email = serializers.EmailField(allow_null=True)
    numero_telephone = serializers.CharField()
    date_inscription = serializers.DateTimeField()

class ErrorResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
    errors = serializers.DictField(required=False)

from rest_framework import serializers
from phonenumber_field.serializerfields import PhoneNumberField


class ModifierProfileClientSerializer(serializers.Serializer):
    numero_telephone = PhoneNumberField(region="DZ")
    code_ticket = serializers.CharField()

    nouveau_numero_telephone = PhoneNumberField(
        region="DZ",
        required=False,
        allow_null=True
    )

    nom = serializers.CharField(required=False, allow_blank=True)
    prenom = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)

    #  Validation du numéro (forcer +213)
    def validate_numero_telephone(self, value):
        if not str(value).startswith("+213"):
            raise serializers.ValidationError(
                "Le numéro de téléphone doit être au format algérien (+213)"
            )
        return value

    def validate_code_ticket(self, value):
        pattern = r"^CTK-(\d{8})-(\d{4})$"
        match = re.match(pattern, value)

        if not match:
            raise serializers.ValidationError(
                "Format invalide. Exemple : CTK-20260427-0001"
            )

        date_part = match.group(1)

        try:
            datetime.strptime(date_part, "%Y%m%d")
        except ValueError:
            raise serializers.ValidationError("Date invalide dans le code ticket")

        return value
