from rest_framework import serializers


class AfficherPlanningMoisSerializer(serializers.Serializer):
    date = serializers.DateField(help_text="Date du jour")
    jour = serializers.CharField(help_text="Nom du jour (DIMANCHE, LUNDI, ...)")
    type = serializers.CharField(help_text="Type du jour : travail | repos | exception")