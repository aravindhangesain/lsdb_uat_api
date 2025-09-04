from rest_framework import serializers
from lsdb.models import *

class StressRunResultSerializer(serializers.ModelSerializer):

    sub_asset_details = serializers.SerializerMethodField()

    def get_sub_asset_details(self, obj):
        sub_asset_details=[]
        stress_run_details=StressRunDetails.objects.filter(stress_run_result=obj.id)
        for detail in stress_run_details:
            sub_asset_details.append({
                "id": detail.sub_asset.id,
                "name": detail.sub_asset.name
            })  
        return sub_asset_details   
    class Meta:
        model = StressRunResult
        fields = ['id', 'run_name', 'step_result', 'asset', 'user', 'run_date','sub_asset_details','comment']