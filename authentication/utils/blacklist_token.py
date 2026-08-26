from rest_framework_simplejwt.tokens import RefreshToken, AccessToken, TokenError
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken

def blacklist_current_and_or_all_tokens(user, raw_token_string=None, blacklist_all=False):
    """
    Essaye de blacklister :
     - le refresh token passé en raw_token_string (si c'est un refresh valide),
     - et/ou tous les outstanding refresh tokens de l'utilisateur (si blacklist_all=True).
    """

    # 1) Si on a reçu un token brut, on tente de le traiter comme refresh et de le blacklist
    if raw_token_string:
        try:
            # Tenter comme RefreshToken — marche si raw_token_string est un refresh token
            rt = RefreshToken(raw_token_string)
            try:
                rt.blacklist()  # méthode simple fournie par simplejwt
            except Exception:
                # Dans de rares cas la blacklisting via rt.blacklist() peut échouer
                # (par ex. l'objet OutstandingToken pas trouvé). On tente fallback.
                jti = rt.get("jti")
                if jti:
                    outstanding = OutstandingToken.objects.filter(jti=jti).first()
                    if outstanding:
                        BlacklistedToken.objects.get_or_create(token=outstanding)
        except TokenError:
            # le token fourni n'est pas un refresh valide — on ignore silencieusement
            pass
        except Exception:
            # autre erreur (par ex. token_blacklist non installé) -> on ignore pour éviter crash
            pass

    # 2) Optionnel : blacklister *tous* les refresh tokens "outstanding" de l'utilisateur
    if blacklist_all:
        try:
            for outstanding in OutstandingToken.objects.filter(user=user):
                BlacklistedToken.objects.get_or_create(token=outstanding)
        except Exception:
            # si token_blacklist non installé ou autre erreur, on ignore
            pass
