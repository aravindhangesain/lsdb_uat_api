from rest_framework import viewsets

from lsdb.models import AuthUser_pichina
from lsdb.serializers import AuthUser_pichinaSerializer

class AuthUser_pichinaViewSet(viewsets.ModelViewSet):
    queryset = AuthUser_pichina.objects.all()
    serializer_class = AuthUser_pichinaSerializer
