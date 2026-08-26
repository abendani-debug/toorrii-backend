from rest_framework import serializers


class ProfessionnelCheckNomEntrepriseSerializer(serializers.Serializer):

    nom_entreprise = serializers.CharField(
        required=True,
        max_length=100
    )