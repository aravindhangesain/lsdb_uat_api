from lsdb.models import *
from rest_framework import serializers
from django.db import IntegrityError, transaction
from django.utils import timezone
from django.db.models import Q, Max
from django.utils import timezone


class EolQueueSerializer(serializers.HyperlinkedModelSerializer):

    
    disposition_name=serializers.ReadOnlyField(source='disposition.name')
    units=serializers.SerializerMethodField()
    customer_name=serializers.ReadOnlyField(source='project.customer.name')

    project_number=serializers.ReadOnlyField(source='project.number')
    days_since_eolready=serializers.SerializerMethodField()
    eol_ready_on=serializers.SerializerMethodField()

    
    def get_units(self, obj):

        units=[]
        for unit in obj.units.all():
            
            var=ProcedureResult.objects.filter(unit_id=unit.id).last()
            completion_date = None
            if var:
                completion_date = MeasurementResult.objects.filter(
                    step_result__procedure_result=var
                ).order_by('-date_time').values_list('date_time', flat=True).first()

            units.append({
                "unit_id": unit.id,
                "unit_disposition":unit.disposition.name,
                "serial_number": unit.serial_number,
                "location_name": unit.location.name if unit.location else None,
                "test_sequence_definition_name": var.test_sequence_definition.name if var and var.test_sequence_definition else None,
                "linear_execution_group": var.linear_execution_group if var else None,
                "completion_date": completion_date
            })
        return units
    
    def get_days_since_eolready(self,obj):
        
        var=WorkOrderUpdateHistory.objects.filter(work_order_id=obj.id,disposition_id=96).order_by('-datetime').first()
        if var:
            days = (timezone.now() - var.datetime).days
            return days
        else:
            return None
    def get_eol_ready_on(self,obj):
        var=WorkOrderUpdateHistory.objects.filter(work_order_id=obj.id,disposition_id=96).order_by('-datetime').first()
        if var:
            return var.datetime
        else:
            return None


    class Meta:
        
        model=WorkOrder
        fields=[
            'id',
            'url',
            'name',
            'customer_name',
            'disposition',
            'disposition_name',
            'project_number',
            "days_since_eolready",
            "eol_ready_on",
            'units'
        ]
