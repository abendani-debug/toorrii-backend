from rest_framework import serializers
from rest_framework import serializers
from adminToorrii.models import Professionnel

class GoogleOAuthSerializer(serializers.Serializer):
    id_token = serializers.CharField(
        required=True
    )



class CompleteProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Professionnel
        fields = [
            "nom_entreprise",
            "numero_telephone",
            "adresse",
            "wilaya",
            "description",
            "logo",
            "confirmation_rdv_auto",
            "theme_couleur",
            "siteweb",
            "facebook",
            "tiktok",
            "instagram",
        ]

    def validate_nom_entreprise(self, value):
        """
        Transforme le nom de l'entreprise en majuscule avant de sauvegarder.
        """
        return value.upper()
    
    def validate_wilaya(self, value):
        import json
        if isinstance(value, str):
            try:
                value = json.loads(value)
            except (json.JSONDecodeError, ValueError):
                raise serializers.ValidationError("Wilaya doit être une liste JSON valide.")
        if not isinstance(value, list):
            raise serializers.ValidationError("Wilaya doit être une liste.")
        return [str(w).upper() for w in value]