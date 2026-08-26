from rest_framework.permissions import BasePermission

class IsAdminUserCustom(BasePermission):
    """
    Autorise uniquement les utilisateurs ayant un profil Admin actif.
    """

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        # Vérifie s'il existe un profil Admin lié
        admin_profile = getattr(user, "admin_profile", None)
        if not admin_profile:
            return False

        # Vérifie si le compte admin est actif
        if admin_profile.etat_compte != "A":
            return False

        return True


class IsProfessionnelUserCustom(BasePermission):
    """
    Autorise uniquement les utilisateurs ayant un profil Professionnel actif.
    """

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            print("NOT AUTHENTICATED")
            return False

        # Vérifie s'il existe un profil Professionnel lié
        professionnel_profile = getattr(user, "professionnel_profile", None)
        print("PRO:", professionnel_profile)
        if not professionnel_profile:
            print("NO PROFILE")
            return False

        print("ETAT:", professionnel_profile.etat_compte)
        print("VERIF:", professionnel_profile.compte_verification)

        # Vérifie si le compte professionnel est actif
        if getattr(professionnel_profile, "etat_compte", None) != "A":
            print("NOT ACTIVE")
            return False

        # Vérifie si le email professionnel est vérifié
        if not getattr(professionnel_profile, "compte_verification", False):
            print("NOT VERIFIED")
            return False    

        return True        