from rest_framework_simplejwt.tokens import RefreshToken

def generate_token_client(client):
    refresh = RefreshToken()

    refresh['client_id'] = client.id_client
    refresh['numero_telephone'] = str(client.numero_telephone)

    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }