from rest_framework import serializers
from lsdb.models import IAMFileRead

class IAMFileReadSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = IAMFileRead
        fields ='__all__'