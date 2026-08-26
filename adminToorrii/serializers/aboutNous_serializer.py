from rest_framework import serializers
from adminToorrii.models import AboutNous

class AboutNousAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = AboutNous   
        fields = "__all__"
        read_only_fields = ['about_id', 'date_creation', 'historique_modifications']

    REQUIRED_KEYS = {
        "titre": {"fr", "en", "ar"},
        "slogan": {"fr", "en", "ar"}, 
        "contenu": {"fr", "en", "ar"},
        "mission": {"fr", "en", "ar"},
        "vision": {"fr", "en", "ar"},
        "valeurs": {"fr", "en", "ar"},
        "pourquoi_choisir_nous": {"fr", "en", "ar"},
        "qui_nous_servons": {"fr", "en", "ar"}
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
    
    def validate_slogan(self, value):
        return self.validate_field_with_keys("slogan", value)
    
    def validate_contenu(self, value):
        return self.validate_field_with_keys("contenu", value)
    
    def validate_mission(self, value):
        return self.validate_field_with_keys("mission", value)
    
    def validate_vision(self, value):
        return self.validate_field_with_keys("vision", value)
    
    def validate_valeurs(self, value):
        return self.validate_field_with_keys("valeurs", value)
    
    def validate_pourquoi_choisir_nous(self, value):
        return self.validate_field_with_keys("pourquoi_choisir_nous", value)    
    
    def validate_qui_nous_servons(self, value):
        return self.validate_field_with_keys("qui_nous_servons", value)

class AboutNousPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = AboutNous
        fields = [
            "titre",
            "slogan",
            "contenu",
            "mission",
            "vision",
            "valeurs",
            "pourquoi_choisir_nous",
            "qui_nous_servons",
            "version"
        ]