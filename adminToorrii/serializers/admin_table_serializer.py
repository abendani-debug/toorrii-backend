from rest_framework import serializers
from adminToorrii.models import AdminUser

class AdminAccountAfficherSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminUser
        fields = [
            "nom",
            "email",
            "numero_telephone",
            "niveau_acces",
            "est_super_admin",
            "etat_compte",
            "date_creation",
        ]
        read_only_fields = fields

class AdminAccountModifierPasswordSerializer(serializers.ModelSerializer):

    class Meta:
        model = AdminUser
        fields = ["nom", "numero_telephone", "password", "email"]
        read_only_fields = ["email"]
        extra_kwargs = {
            "password": {"write_only": True}
        }

    def validate_numero_telephone(self, value):
        if AdminUser.objects.exclude(admin_id=self.instance.admin_id).filter(numero_telephone=value).exists():
            raise serializers.ValidationError("Ce numéro de téléphone est déjà utilisé.")
        return value

    def update(self, instance, validated_data):
        if "password" in validated_data:
            password = validated_data.pop("password")
            instance.set_password(password)
        return super().update(instance, validated_data)    

class AdminAccountModifierSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdminUser
        fields = [
            "nom",
            "numero_telephone",
            "password",
            "email",  # lu mais jamais modifiable
        ]
        read_only_fields = ["email"]  # email non modifiable

    def validate_numero_telephone(self, value):
        if AdminUser.objects.exclude(admin_id=self.instance.admin_id).filter(numero_telephone=value).exists():
            raise serializers.ValidationError("Ce numéro de téléphone est déjà utilisé.")
        return value
        
    def update(self, instance, validated_data):
        if "password" in validated_data:
            password = validated_data.pop("password")
            instance.set_password(password)
        return super().update(instance, validated_data)