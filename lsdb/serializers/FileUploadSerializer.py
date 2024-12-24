from rest_framework import serializers
from lsdb.models import AzureFile

class FileUploadSerializer(serializers.ModelSerializer):
    file = serializers.FileField()
    cropped_file = serializers.FileField()
    procedure_result_id = serializers.IntegerField(required=False, allow_null=True)
    exposure_count = serializers.FloatField(required=False, allow_null=True)
    iso = serializers.FloatField(required=False, allow_null=True)
    aperture = serializers.FloatField(required=False, allow_null=True)
    injection_current = serializers.FloatField(required=False, allow_null=True)
    exposure_time = serializers.FloatField(required=False, allow_null=True)

    class Meta:
        model = AzureFile
        fields = [
            'file',
            'cropped_file',
            'procedure_result_id',
            'exposure_count',
            'iso',
            'aperture',
            'injection_current',
            'exposure_time'
        ]