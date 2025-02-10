from rest_framework import serializers
from lsdb.models import TemplateDetails

class TemplateDetailsSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model=TemplateDetails
        fields='__all__'