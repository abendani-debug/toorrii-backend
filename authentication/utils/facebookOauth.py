import requests
from django.conf import settings
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken


def verify_facebook_token(access_token):
    url = "https://graph.facebook.com/debug_token"

    params = {
        "input_token": access_token,
        "access_token": f"{settings.FACEBOOK_APP_ID}|{settings.FACEBOOK_APP_SECRET}"
    }

    response = requests.get(url, params=params)
    data = response.json()

    return data.get("data", {}).get("is_valid", False)


def blacklist_existing_refresh_tokens(user):
    tokens = OutstandingToken.objects.filter(user=user)
    for token in tokens:
        BlacklistedToken.objects.get_or_create(token=token)