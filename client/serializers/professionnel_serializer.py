from rest_framework import serializers


class ProfessionnelFullSerializer(serializers.Serializer):
    professionnel_id = serializers.CharField()
    nom_entreprise = serializers.CharField()
    email = serializers.EmailField()
    numero_telephone = serializers.CharField()
    adresse = serializers.CharField()
    wilaya = serializers.JSONField()
    description = serializers.CharField()

    logo = serializers.ImageField()
    code_qr = serializers.ImageField(allow_null=True)


    theme_couleur = serializers.CharField()
    date_inscription = serializers.DateTimeField()

    nombre_priorite = serializers.IntegerField()

    siteweb = serializers.URLField(allow_null=True)
    facebook = serializers.URLField(allow_null=True)
    tiktok = serializers.URLField(allow_null=True)
    instagram = serializers.URLField(allow_null=True)