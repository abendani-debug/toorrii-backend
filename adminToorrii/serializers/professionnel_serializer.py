from rest_framework import serializers
from django.db import transaction
from adminToorrii.utils.brevo_service import send_register_notification_professionnel_par_admin
from adminToorrii.models import Professionnel, Utilisateur
from adminToorrii.models.categorie import Categorie


class NullableCategorieField(serializers.PrimaryKeyRelatedField):
    """Permet d'envoyer une chaîne vide pour effacer la spécialité (retourne None)."""
    def to_internal_value(self, data):
        if data == '' or data is None:
            return None
        return super().to_internal_value(data)


class ProfessionnelSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        min_length=6,
        max_length=30,
        style={'input_type': 'password'},
        required=False
    )
    specialite = NullableCategorieField(
        queryset=Categorie.objects.all(),
        allow_null=True,
        required=False,
    )
    specialite_nom = serializers.SerializerMethodField(read_only=True)

    def get_specialite_nom(self, obj):
        if obj.specialite:
            nom = obj.specialite.nom_categorie
            if isinstance(nom, dict):
                return nom.get('fr') or nom.get('en') or nom.get('ar') or ''
            return str(nom)
        return None

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
            "compte_verification",
            "nombre_sms",
            "nombre_priorite",
            "confirmation_rdv_auto",
            "theme_couleur",
            "etat_compte",
            "siteweb",
            "facebook",
            "tiktok",
            "instagram",
            "password",
            "code_qr",
            "date_creation",
            "professionnel_id",
            "specialite",
            "specialite_nom",
        ]
        read_only_fields = ["professionnel_id", "code_qr", "date_creation", "specialite_nom"]

    # =========================
    # VALIDATION EMAIL
    # =========================
    def validate_email(self, value):
        instance = getattr(self, "instance", None)

        if instance:
            # UPDATE
            if Professionnel.objects.exclude(pk=instance.pk).filter(email=value).exists():
                raise serializers.ValidationError(
                    "Un autre compte utilise déjà cet email."
                )
        else:
            # CREATE
            if Professionnel.objects.filter(email=value).exists():
                raise serializers.ValidationError(
                    "Un compte avec cet email existe déjà."
                )

        return value

    # =========================
    # NOM ENTREPRISE
    # =========================
    def validate_nom_entreprise(self, value):
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

    # =========================
    # CREATE
    # =========================
    @transaction.atomic
    def create(self, validated_data):
        password = validated_data.pop("password", None)

        email = validated_data.get("email")

        # 1. Création utilisateur
        utilisateur = Utilisateur.objects.create_professionnel(
            email=email,
            password=password
        )

        # 2. Création professionnel
        professionnel = Professionnel.objects.create(
            utilisateur=utilisateur,
            **validated_data
        )

        # 3. Email notification
        try:
            send_register_notification_professionnel_par_admin(
                email=professionnel.email,
                nom=professionnel.nom_entreprise,
            )
        except Exception:
            pass

        return professionnel

    # =========================
    # UPDATE
    # =========================
    @transaction.atomic
    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        email = validated_data.get("email", None)

        # -------------------------
        # UPDATE EMAIL + USER
        # -------------------------
        if email:
            if Professionnel.objects.exclude(pk=instance.pk).filter(email=email).exists():
                raise serializers.ValidationError({
                    "email": "Un autre compte utilise déjà cet email."
                })

            instance.utilisateur.email = email
            instance.utilisateur.username = email
            instance.utilisateur.save()

        # -------------------------
        # UPDATE PROFESSIONNEL FIELDS
        # -------------------------
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        # -------------------------
        # UPDATE PASSWORD
        # -------------------------
        if password:
            instance.utilisateur.set_password(password)
            instance.utilisateur.save()

        return instance