from rest_framework import serializers
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError as DjangoValidationError
from adminToorrii.models import Partenaire


class PartenaireAdminSerializer(serializers.ModelSerializer):

    class Meta:
        model = Partenaire
        fields = "__all__"
        read_only_fields = ["partenaire_id", "date_ajout"]

    REQUIRED_KEYS = {
        "nom_partenaire": {"fr", "en", "ar"},
        "description": {"fr", "en", "ar"}
    }

    # Validation générique des champs multilingues
    def validate_field_with_keys(self, field_name, value):

        if not isinstance(value, dict):
            raise serializers.ValidationError(
                f"Le champ '{field_name}' doit être un dictionnaire."
            )

        required_keys = self.REQUIRED_KEYS.get(field_name, set())
        missing_keys = required_keys - value.keys()

        if missing_keys:
            raise serializers.ValidationError(
                f"Le champ '{field_name}' doit contenir les clés obligatoires : {', '.join(missing_keys)}"
            )

        return value

    # Validation nom_partenaire
    def validate_nom_partenaire(self, value):
        return self.validate_field_with_keys("nom_partenaire", value)

    # Validation description
    def validate_description(self, value):
        return self.validate_field_with_keys("description", value)

    # Validation liens_externes (facultatif)
    def validate_liens_externes(self, value):

        # Champ facultatif
        if value in [None, {}, []]:
            return value

        if not isinstance(value, dict):
            raise serializers.ValidationError(
                "Le champ 'liens_externes' doit être un dictionnaire."
            )

        validator = URLValidator()

        for key, url in value.items():

            if not key:
                raise serializers.ValidationError(
                    "Chaque lien externe doit avoir une clé."
                )

            try:
                validator(url)
            except DjangoValidationError:
                raise serializers.ValidationError(
                    f"L'URL '{url}' dans 'liens_externes' est invalide."
                )

        return value

class PartenairePublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Partenaire
        fields = [
            "partenaire_id",
            "nom_partenaire",
            "logo",
            "description",
            "adresse",
            "email",
            "telephone",
            "type_partenaire",
            "site_web",
            "image_banniere",
            "priorite_affichage",   
            "facebook",
            "instagram",
            "tiktok",
            "liens_externes",
            "date_creation_entreprise"
        ]