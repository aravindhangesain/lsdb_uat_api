from rest_framework import serializers
from lsdb.models import MeasurementResult
from lsdb.models import AzureFile
from lsdb.serializers.AzureFileSerializer import AzureFileSerializer
from lsdb.utils.Limits import within_limits


class MeasurementResultSerializer(serializers.HyperlinkedModelSerializer):
    result_files = AzureFileSerializer(AzureFile.objects.all(), many=True, read_only=True)
    measurement_result_type_field = serializers.ReadOnlyField(source='measurement_result_type.name')
    result_defect_name = serializers.ReadOnlyField(source='result_defect.short_name')
    within_limits = serializers.SerializerMethodField()

    def get_within_limits(self, obj):
        return (within_limits(obj))



    class Meta:
        model = MeasurementResult
        fields = [
            'id',
            'url',
            'date_time',
            'step_result',
            'measurement_definition',
            'user',
            'location',
            # This is a string until I find better info
            'software_revision',
            'disposition',
            # 'disposition_codes',
            'result_defect',
            'result_defect_name',
            'result_double',
            'result_datetime',
            'result_string',
            'result_boolean',
            # TODO: ResultGuid -- Link to another table, table defined in measurement result type
            'limit',
            # 'out_of_family_limit',
            # check reviewed_by_user for duplication (lsdb has 2 for no good reason)
            'reviewed_by_user',
            'review_datetime',
            'notes',
            # Do we want actual tags?
            'tag',
            'station',
            'start_datetime',
            'duration',
            'asset',
            'do_not_include',
            'name',
            'record_only',
            'allow_skip',
            'requires_review',
            'measurement_type',
            # 'apply_out_of_family_limit',
            'order',
            'report_order',
            'measurement_result_type',
            'measurement_result_type_field',
            'within_limits',
            'result_files',
        ]
        read_only_fields =[
            'within_limits',
            'result_files',
        ]

class MeasurementResultStressSerializer(serializers.HyperlinkedModelSerializer):
    result_files = AzureFileSerializer(AzureFile.objects.all(), many=True, read_only=True)
    measurement_result_type_field = serializers.ReadOnlyField(source='measurement_result_type.name')
    result_defect_name = serializers.ReadOnlyField(source='result_defect.short_name')
    within_limits = serializers.SerializerMethodField()
    username = serializers.ReadOnlyField(source='user.username')
    asset_name = serializers.ReadOnlyField(source='asset.name')

    def get_within_limits(self, obj):
        return (within_limits(obj))

    class Meta:
        model = MeasurementResult
        fields = [
            'id',
            'url',
            'date_time',
            'step_result',
            'measurement_definition',
            'username',
            'location',
            # This is a string until I find better info
            'software_revision',
            'disposition',
            # 'disposition_codes',
            'result_defect',
            'result_defect_name',
            'result_double',
            'result_datetime',
            'result_string',
            'result_boolean',
            # TODO: ResultGuid -- Link to another table, table defined in measurement result type
            'limit',
            # 'out_of_family_limit',
            # check reviewed_by_user for duplication (lsdb has 2 for no good reason)
            'reviewed_by_user',
            'review_datetime',
            'notes',
            # Do we want actual tags?
            'tag',
            'station',
            'start_datetime',
            'duration',
            'asset_name',
            'do_not_include',
            'name',
            'record_only',
            'allow_skip',
            'requires_review',
            'measurement_type',
            # 'apply_out_of_family_limit',
            'order',
            'report_order',
            'measurement_result_type',
            'measurement_result_type_field',
            'within_limits',
            'result_files',
        ]
        read_only_fields =[
            'within_limits',
            'result_files',
        ]
