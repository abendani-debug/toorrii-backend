from rest_framework import serializers
from adminToorrii.models import Categorie


class CategorieEnfantSerializer(serializers.ModelSerializer):
    """Serializer léger pour les enfants imbriqués (niveaux 2 et 3)."""
    enfants = serializers.SerializerMethodField()

    class Meta:
        model = Categorie
        fields = [
            "categorie_id",
            "nom_categorie",
            "description_categorie",
            "couleur_theme",
            "photo_principale_cat",
            "ordre_affichage",
            "niveau",
            "active",
            "enfants",
        ]

    def get_enfants(self, obj):
        children = obj.enfants.all().order_by("ordre_affichage")
        return CategorieEnfantSerializer(children, many=True, context=self.context).data


class CategorieAfficherSerializer(serializers.ModelSerializer):
    """Serializer lecture complète avec arborescence imbriquée."""
    enfants = serializers.SerializerMethodField()

    class Meta:
        model = Categorie
        fields = [
            "categorie_id",
            "nom_categorie",
            "description_categorie",
            "couleur_theme",
            "photo_principale_cat",
            "ordre_affichage",
            "niveau",
            "active",
            "date_creation",
            "parent",
            "enfants",
        ]

    def get_enfants(self, obj):
        children = obj.enfants.all().order_by("ordre_affichage")
        return CategorieEnfantSerializer(children, many=True, context=self.context).data


class CategorieSerializer(serializers.ModelSerializer):
    """Serializer création/modification."""

    class Meta:
        model = Categorie
        fields = [
            "nom_categorie",
            "description_categorie",
            "couleur_theme",
            "ordre_affichage",
            "photo_principale_cat",
            "active",
            "categorie_id",
            "date_creation",
            "parent",
            "niveau",
        ]
        read_only_fields = ["categorie_id", "date_creation", "niveau"]

    def validate(self, attrs):
        parent = attrs.get("parent")
        if parent and parent.niveau >= 3:
            raise serializers.ValidationError(
                {"parent": "Impossible de créer un niveau 4. La hiérarchie est limitée à 3 niveaux."}
            )
        return attrs
