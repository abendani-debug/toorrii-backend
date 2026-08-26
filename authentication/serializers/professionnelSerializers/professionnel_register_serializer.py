from rest_framework import serializers
from authentication.utils.professionnel_utils import generate_otp, send_register_notification_professionnel
from adminToorrii.models import Professionnel, Utilisateur



class ProfessionnelRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        min_length=6,
        max_length=30,
        style={'input_type': 'password'},
    )

    class Meta:
        model = Professionnel
        fields = [
            "nom_entreprise",
            "email",
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
            "password"
        ]
        extra_kwargs = {
            "numero_telephone": {
                "error_messages": {
                    "unique": "Ce numéro a déjà été utilisé."
                }
            },
            "email": {
                "error_messages": {
                    "unique": "Un compte avec cet email existe déjà."
                }
            },
        }

    def validate_email(self, value):
        """
        Vérifie que l'email n'existe pas déjà.
        """
        if Professionnel.objects.filter(email=value).exists():
            raise serializers.ValidationError("Un compte avec cet email existe déjà.")
        return value

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

    def create(self, validated_data):
        """
        Création du professionnel et de l'utilisateur lié :
        1. Génère un OTP et le stocke
        2. Crée le Professionnel
        3. Crée un Utilisateur lié via `create_professionnel`
        4. Envoie un email avec le code OTP
        """
        password = validated_data.pop("password")  # Retirer le mot de passe du dict pour Professionnel

        # 1 Génération OTP
        otp = generate_otp()
        validated_data["code_verification"] = otp

        email = validated_data.get("email")

        # 2 Création de l'utilisateur lié
        utilisateur = Utilisateur.objects.create_professionnel(
            email=email,
            password=password
        )
        # 3 Création du professionnel
        professionnel = Professionnel.objects.create(utilisateur=utilisateur, **validated_data)


        # 4 Envoi email via Brevo
        try:
            send_register_notification_professionnel(
                email=professionnel.email,
                nom_entreprise=professionnel.nom_entreprise,
                otp=otp
            )
            professionnel.nombre_send_email += 1
            professionnel.save(update_fields=["nombre_send_email"])
        except Exception as e:
            # Ici tu peux logger l'erreur ou gérer un rollback
            pass

        return professionnel