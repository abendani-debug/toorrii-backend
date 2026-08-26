from rest_framework_simplejwt.tokens import RefreshToken
from datetime import datetime, timedelta
import jwt
from django.conf import settings
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken


def generate_jwt_for_email(email: str):
    payload = {
        "email": email,
        "exp": datetime.utcnow() + timedelta(hours=1),  # token valide 1h
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
    return token



def get_tokens_for_user_admin(utilisateur):
    """
    Génère des tokens JWT pour un utilisateur admin avec claims personnalisés.
    `utilisateur` doit être une instance de Utilisateur.
    """
    refresh = RefreshToken.for_user(utilisateur)
    
    # Claims personnalisés
    refresh['user_id'] = utilisateur.utilisateur_id
    refresh['email'] = utilisateur.email
    refresh['role'] = 'admin'
    
    access_token = str(refresh.access_token)
    refresh_token = str(refresh)

    return {
        'access': access_token,
        'refresh': refresh_token
    }

def blacklist_existing_refresh_tokens(user):
    tokens = OutstandingToken.objects.filter(user=user)
    for token in tokens:
        BlacklistedToken.objects.get_or_create(token=token)


def get_tokens_for_user_professionnel(utilisateur):
    """
    Génère access + refresh token avec rotation + blacklist + claims personnalisés
    """

    #  1. Blacklist anciens tokens
    blacklist_existing_refresh_tokens(utilisateur)

    #  2. Générer nouveau refresh
    refresh = RefreshToken.for_user(utilisateur)

    #  3. Ajouter claims personnalisés
    refresh['user_id'] = utilisateur.utilisateur_id   
    refresh['email'] = utilisateur.email
    refresh['role'] = 'professionnel'

    return {
        'access': str(refresh.access_token),
        'refresh': str(refresh)
    }    


def decode_token(token):
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
