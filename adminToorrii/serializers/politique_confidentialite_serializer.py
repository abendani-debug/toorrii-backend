from rest_framework import serializers
from adminToorrii.models import PolitiqueConfidentialite

class PolitiqueConfidentialiteAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = PolitiqueConfidentialite
        fields = "__all__"  # Tous les champs
        read_only_fields = ["politique_id", "date_creation", "historiqueModifications"]

    REQUIRED_KEYS = {
        "titre": {"fr", "en", "ar"},
        "contenu": {"fr", "en", "ar"}, 
    }
    # Validation générique

    def validate_field_with_keys(self, field_name, value):
        required_keys = self.REQUIRED_KEYS.get(field_name, set())
        missing_keys = required_keys - value.keys()
        if missing_keys:
            raise serializers.ValidationError(
                f"Le champ '{field_name}' doit contenir les clés obligatoires : {', '.join(missing_keys)}"
            )
        return value

    # Méthodes de validation DRF pour chaque champ

    def validate_titre(self, value):
        return self.validate_field_with_keys("titre", value)
    def validate_contenu(self, value):
        return self.validate_field_with_keys("contenu", value)

class PolitiqueConfidentialitePublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = PolitiqueConfidentialite
        fields = [
            "titre",
            "contenu",
            "version",
        ]
