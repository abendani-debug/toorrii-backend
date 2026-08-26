from rest_framework import serializers

class AfficherCreneauxSerializer(serializers.Serializer):
    debut = serializers.TimeField()
    fin = serializers.TimeField()
    type = serializers.ChoiceField(choices=["disponible", "reserve", "pause"])