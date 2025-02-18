from rest_framework import serializers
from lsdb.models import ProductTypeDefinition

class ProductTypeDefinitionSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model=ProductTypeDefinition
        fields=[
            'id',
            'url',
            'name',
            'linear_execution_order',
            'group',
            'disposition',
            'version'
        ]