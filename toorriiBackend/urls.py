from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
   path('admin/', admin.site.urls),
   path('api/auth/', include('authentication.urls')),
   path('api/admin/', include('adminToorrii.urls')),
   path('api/professionnel/', include('professionnel.urls')),
   path('api/client/', include('client.urls')),
   path('api/home/', include('home.urls')),
   
   

    # Swagger UI
   path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
   path('api/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )