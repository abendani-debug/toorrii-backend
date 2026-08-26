from rest_framework import serializers

class LoginProfessionnelSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

class ProfessionnelLoginResponseSerializer(serializers.Serializer):
    professionnel_id = serializers.CharField()
    email = serializers.EmailField()
    nom = serializers.CharField()
    access = serializers.CharField()