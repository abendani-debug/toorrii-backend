from rest_framework import serializers

class FacebookOAuthSerializer(serializers.Serializer):
    access_token = serializers.CharField()