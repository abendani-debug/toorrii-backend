from rest_framework import serializers
from adminToorrii.models import Categorie


class CategorieNiveau3Serializer(serializers.ModelSerializer):
    """Sous-catégories (niveau 3) — affichage côté client."""
    class Meta:
        model = Categorie
        fields = [
            "categorie_id",
            "nom_categorie",
            "couleur_theme",
            "photo_principale_cat",
            "ordre_affichage",
        ]


class CategorieNiveau2Serializer(serializers.ModelSerializer):
    """Catégories (niveau 2) avec leurs sous-catégories imbriquées."""
    enfants = serializers.SerializerMethodField()

    class Meta:
        model = Categorie
        fields = [
            "categorie_id",
            "nom_categorie",
            "ordre_affichage",
            "enfants",
        ]

    def get_enfants(self, obj):
        children = obj.enfants.filter(active=True).order_by("ordre_affichage")
        return CategorieNiveau3Serializer(children, many=True, context=self.context).data


class CategorieAfficherSerializer(serializers.ModelSerializer):
    """Secteurs (niveau 1) avec arborescence complète — navigation client."""
    enfants = serializers.SerializerMethodField()

    class Meta:
        model = Categorie
        fields = [
            "categorie_id",
            "nom_categorie",
            "couleur_theme",
            "photo_principale_cat",
            "ordre_affichage",
            "enfants",
        ]

    def get_enfants(self, obj):
        children = obj.enfants.filter(active=True).order_by("ordre_affichage")
        return CategorieNiveau2Serializer(children, many=True, context=self.context).data
