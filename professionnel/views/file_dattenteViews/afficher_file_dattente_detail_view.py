from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from adminToorrii.models import FileDattente, Professionnel
from adminToorrii.permissions import IsProfessionnelUserCustom
from professionnel.serializers import FileDattenteDetailSerializer


class AfficherFileDattenteDetailView(APIView):

    permission_classes = [IsProfessionnelUserCustom]

    @extend_schema(
        tags=["File d'attente Professionnel"],
        summary="Détail d'une file d'attente (professionnel)",
        description="""
Retourne le détail d'une file d'attente.

 Sécurité :
- Accessible uniquement au professionnel connecté
- Le file_id doit appartenir à ses services

 Retourne :
- Infos file
- Service associé
- Nombre de clients
""",
        parameters=[
            OpenApiParameter(
                name="file_id",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
                description="ID de la file d'attente (ex: FILE_1)"
            )
        ],
        responses={200: FileDattenteDetailSerializer}
    )
    def get(self, request, file_id):

        utilisateur = request.user

        # récupérer professionnel connecté
        try:
            professionnel = utilisateur.professionnel_profile
        except Professionnel.DoesNotExist:
            return Response(
                {"error": "Profil professionnel introuvable"},
                status=status.HTTP_404_NOT_FOUND
            )

        # récupérer file avec sécurité
        try:
            file = FileDattente.objects.select_related(
                "service", "professionnel"
            ).get(
                file_id=file_id,
                professionnel=professionnel
            )
        except FileDattente.DoesNotExist:
            return Response(
                {"error": "File d'attente introuvable ou non autorisée"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = FileDattenteDetailSerializer(file)

        return Response(serializer.data, status=status.HTTP_200_OK)