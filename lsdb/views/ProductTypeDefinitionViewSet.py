from rest_framework import viewsets
from lsdb.models import ProductTypeDefinition
from lsdb.serializers import ProductTypeDefinitionSerializer


class ProductTypeDefinitionViewSet(viewsets.ModelViewSet):
    queryset = ProductTypeDefinition.objects.all()
    serializer_class = ProductTypeDefinitionSerializer