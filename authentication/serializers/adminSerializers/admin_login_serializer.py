from rest_framework import serializers
from adminToorrii.models.adminTable import AdminUser

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(
        error_messages = {
        'required' : 'Email est obligatoire.',
        'invalid' : 'Veuillez saisir une adresse e-mail valide.'
    })
    password = serializers.CharField(
        write_only = True,
        min_length = 6,
        max_length = 30,
        style = {'input_type' : 'password'},
    )
class AdminLoginResponseSerializer(serializers.Serializer):
    admin_id = serializers.CharField()
    email = serializers.EmailField()
    nom = serializers.CharField()
    access = serializers.CharField()
    
