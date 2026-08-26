from rest_framework.exceptions import AuthenticationFailed
from adminToorrii.models import Client

def get_client_from_request(request):
    auth = request.headers.get("Authorization")

    if not auth or not auth.startswith("ClientToken "):
        raise AuthenticationFailed("Token client manquant.")

    token = auth.replace("ClientToken ", "").strip()

    try:
        client = Client.objects.get(token=token, actif=True)
    except Client.DoesNotExist:
        raise AuthenticationFailed("Token invalide ou client inactif.")

    return client
