from rest_framework import serializers
from lsdb.models import CrateIntakeImages




class CrateUpdateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(write_only=False)

    class Meta:
        model=CrateIntakeImages
        fields=[
            'id',
            'newcrateintake',
            'image_path',
            'label_name',
            'notes'
            ]
