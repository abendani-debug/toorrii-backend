from rest_framework import serializers
from adminToorrii.models import Client

class AfficherClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = "__all__"  # Tous les champs seront exposés
