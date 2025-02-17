from rest_framework import serializers
from lsdb.models import ProductTypeDefinition

class ProductTypeDefinitionSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model=ProductTypeDefinition
        fields='__all__'