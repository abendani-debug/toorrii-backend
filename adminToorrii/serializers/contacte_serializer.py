from rest_framework import serializers
from adminToorrii.models import Contacte

class ContacteAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contacte
        fields = "__all__"
        read_only_fields = ["id", "date_creation", "historique_modifications"]

    REQUIRED_KEYS = {
        "adresse": {"fr", "en", "ar"}, 
        "ville": {"fr", "en", "ar"},
        "wilaya": {"fr", "en", "ar"},
        "message_acceuil": {"fr", "en", "ar"}
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
    def validate_adresse(self, value):
        return self.validate_field_with_keys("adresse", value)

    def validate_ville(self, value):
        return self.validate_field_with_keys("ville", value)

    def validate_wilaya(self, value):
        return self.validate_field_with_keys("wilaya", value)

    def validate_message_acceuil(self, value):
        return self.validate_field_with_keys("message_acceuil", value)

        
class ContactePublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contacte
        fields = [
            "email",
            "telephone_1",
            "telephone_2",
            "telephone_fix",
            "adresse",
            "ville",
            "wilaya",
            "horaires",
            "site_web",
            "facebook",
            "instagram",
            "tiktok",
            "linkedin",
            "x",
            "message_acceuil",
        ]
