from rest_framework import serializers
from adminToorrii.models import Professionnel

class ProfessionnelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Professionnel
        exclude = ["professionnel_id","date_creation", "utilisateur", "compte_verification", "code_verification", "nombre_send_email", "temp_code_verification", "code_verification_reset_password", "nombre_send_email_reset_password", "temp_code_verification_reset_password"]
        read_only_fields = [ "code_qr", "email", "etat_compte", "date_inscription", "nombre_sms", "nombre_priorite"]