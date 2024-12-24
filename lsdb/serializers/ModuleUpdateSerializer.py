from rest_framework import serializers
from lsdb.models import ModuleIntakeImages




class ModuleUpdateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(write_only=False)

    class Meta:
        model=ModuleIntakeImages
        fields=[
            'id',
            'moduleintake',
            'image_path',
            'label_name',
            'notes'
            ]