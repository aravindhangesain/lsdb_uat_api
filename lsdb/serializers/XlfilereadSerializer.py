from rest_framework import serializers
from lsdb.models import Xlfileread

class XlfilereadSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Xlfileread
        fields ='__all__'