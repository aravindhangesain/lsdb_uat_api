from rest_framework import serializers
from lsdb.models import Project,WorkOrder,MeasurementResult
from lsdb.utils.HasHistory import measurements_completed, measurements_requested
from django.db.models import Max

class ActiveProjectsReportSerializer(serializers.ModelSerializer):
    project_manager_name = serializers.ReadOnlyField(source='project_manager.username', read_only=True)
    customer_name = serializers.ReadOnlyField(source='customer.name', read_only=True)
    disposition_name = serializers.ReadOnlyField(source='disposition.name', read_only=True)
    percent_complete = serializers.SerializerMethodField()
    work_order_name = serializers.SerializerMethodField()
    last_action_date =serializers.SerializerMethodField()

    def get_work_order_name(self, obj):
        work_order = WorkOrder.objects.filter(project_id=obj.id, disposition__complete=False).first()
        return work_order.name if work_order else None
      
    def get_percent_complete(self, obj):
        measurements = measurements_requested(obj)
        if measurements == 0:
            return 0
        else:
            return int(100 * (measurements_completed(obj) / measurements))
        
    def get_last_action_date(self, obj):
        # need highest date of completed procedure result
        date_time = MeasurementResult.objects.filter(step_result__procedure_result__unit__project=obj).aggregate(
            Max('date_time'))
        if date_time:
            return date_time["date_time__max"]
        else:
            return None


    class Meta:
        model = Project
        fields = [
            'number',
            'project_manager_name',
            'customer_name',
            'disposition_name',
            'percent_complete',
            'work_order_name',
            'last_action_date'
        ]
