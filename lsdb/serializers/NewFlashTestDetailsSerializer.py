from rest_framework import serializers
from lsdb.models import *

class NewFlashTestDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewFlashTestDetails
        fields = '__all__'