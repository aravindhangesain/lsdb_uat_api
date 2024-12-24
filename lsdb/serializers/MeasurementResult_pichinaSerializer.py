from rest_framework import serializers
from lsdb.models import MeasurementResult_pichina
from lsdb.models import AzureFile_pichina
from lsdb.serializers.AzureFile_pichinaSerializer import AzureFile_pichinaSerializer
# from lsdb.utils.Limits_pichina import within_limits


class MeasurementResult_pichinaSerializer(serializers.HyperlinkedModelSerializer):
    result_files = AzureFile_pichinaSerializer(AzureFile_pichina.objects.all(), many=True, read_only=True)
    measurement_result_type_field = serializers.ReadOnlyField(source='measurement_result_type.name')
    result_defect_name = serializers.ReadOnlyField(source='result_defect.short_name')
    # within_limits = serializers.SerializerMethodField()

    # def get_within_limits(self, obj):
    #     return (within_limits(obj))


    class Meta:
        model = MeasurementResult_pichina
        fields = [
            'id',
            'url',
            'date_time',
            'step_result',
            'measurement_definition',
            'user',
            'location',
            'software_revision',
            'disposition',
            # 'disposition_codes',
            'result_defect',
            'result_defect_name',
            'result_double',
            'result_datetime',
            'result_string',
            'result_boolean',
            # 'limit',
            # 'out_of_family_limit',
            'reviewed_by_user',
            'review_datetime',
            'notes',
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
            # 'within_limits',
            'result_files',
        ]
        # read_only_fields =[
        #     'within_limits',
        #     'result_files',
        # ]


