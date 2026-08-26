from django.urls import path, include
from .views import AdminLoginView, LogoutView
from .views import ProfessionnelRegisterView, ProfessionnelResendOTPView, ProfessionnelVerifyOTPView, ProfessionnelCheckEmailView, ProfessionnelCheckNomEntrepriseView, ProfessionnelResetPasswordRequestView, ProfessionnelResetPasswordVerifyView, AdminResetPasswordRequestView, AdminResetPasswordVerifyView, GoogleOAuthLoginView, CompleteProfileView, GetCSRFToken 
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from .views import RefreshAccessTokenView
from .views import FacebookOAuthLoginView
from .views import ProfessionnelLoginView

urlpatterns = [
    path('admin/login/', AdminLoginView.as_view(), name='admin-login'),
    path('professionnel/login/', ProfessionnelLoginView.as_view(), name='professionnel-login'),
    path('admin/logout/', LogoutView.as_view(), name='admin-logout'),
    path("admin/password/resendOTP/",AdminResetPasswordRequestView.as_view(),name="admin-resend-password-OTP"),
    path("admin/password/verifyOTP/",AdminResetPasswordVerifyView.as_view(),name="admin-verify-password-OTP"),
    path("professionnel/password/resendOTP/",ProfessionnelResetPasswordRequestView.as_view(),name="professionnel-resend-password-OTP"),
    path("professionnel/password/verifyOTP/",ProfessionnelResetPasswordVerifyView.as_view(),name="professionnel-verify-password-OTP"),
    path("token/refresh/", RefreshAccessTokenView.as_view(), name="token-refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token-verify"),
    path("professionnel/register/",ProfessionnelRegisterView.as_view(),name="professionnel-register"),
    path("professionnel/email/resendOTP/",ProfessionnelResendOTPView.as_view(),name="professionnel-resend-OTP"),
    path("professionnel/email/verifyOTP/",ProfessionnelVerifyOTPView.as_view(),name="professionnel-verify-OTP"),
    path("professionnel/password/resendOTP/",ProfessionnelResetPasswordRequestView.as_view(),name="professionnel-resend-password-OTP"),
    path("professionnel/password/verifyOTP/",ProfessionnelResetPasswordVerifyView.as_view(),name="professionnel-verify-password-OTP"),
    path("professionnel/check/email/",ProfessionnelCheckEmailView.as_view(),name="professionnel-check-email"),
    path("professionnel/check/nomEntreprise/",ProfessionnelCheckNomEntrepriseView.as_view(),name="professionnel-check-Nom"),
    path("professionnel/OAuth/google/login/",GoogleOAuthLoginView.as_view(),name="professionnel-check-token"),
    path("professionnel/OAuth/facebook/login/",FacebookOAuthLoginView.as_view(),name="facebook-login"),
    path("professionnel/OAuth/completeProfile/",CompleteProfileView.as_view(),name="professionnel-completeProfile"),

    # OAuth Google 

    path("api/auth/google/", include("allauth.socialaccount.urls")),  # OAuth Google

    #CSRF
    path("token/csrf/", GetCSRFToken.as_view(), name="token-csrf"),

]
