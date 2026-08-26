from rest_framework import serializers

class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField(required=True, help_text="Refresh token à révoquer")

class LogoutResponseSerializer(serializers.Serializer):
    message = serializers.CharField()    
