from rest_framework import serializers
from lsdb.models import TemplateMaster


class TemplateMasterSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model=TemplateMaster
        fields='__all__'