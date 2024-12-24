from rest_framework import serializers
from django.db import transaction
from django.db.models import Max
from django.utils import timezone
from lsdb.utils.HasHistory_pichina import work_order_measurements_completed
from lsdb.models import Unit_pichina, Workorder_pichina



class WorkOrderProject_pichinaSerializer(serializers.ModelSerializer):
    unit_count = serializers.SerializerMethodField()
    percent_complete = serializers.SerializerMethodField()
    last_action_days = serializers.SerializerMethodField()
    last_action_date = serializers.SerializerMethodField()
    disposition_name = serializers.ReadOnlyField(source='disposition.name', read_only=True)

    @transaction.atomic
    def fill_meta(self, obj):
        queryset = obj.procedureresult_pichina_set.filter(stepresult_pichina__measurementresult_pichina__disposition__isnull=False)
        queryset = queryset.annotate(last_result = Max('stepresult_pichina__measurementresult_pichina__date_time'))
        try:
            results, = max(queryset.filter(last_result__isnull=False).values_list('last_result'))
            self.Meta.meta_days = (timezone.now() - results).days
            self.Meta.meta_date = results
        except:
            self.Meta.meta_days = 0
            self.Meta.meta_date = None
        return self.Meta.meta_days, self.Meta.meta_date

    def get_last_action_days(self, obj):
        if self.Meta.meta_days != None:
            return self.Meta.meta_days
        else:
            days, date = self.fill_meta(obj)
            return days

    def get_last_action_date(self, obj):
        if self.Meta.meta_days != None:
            return self.Meta.meta_date
        else:
            days, date = self.fill_meta()
            return date

    def get_unit_count(self, obj):
        return len(obj.get_units())
    

    def get_units(self, obj):
        unit_ids = obj.get_units()
        units = Unit_pichina.objects.filter(id__in=unit_ids)
        return [{'id': unit.id, 'name': unit.name} for unit in units]

    def get_percent_complete(self, obj):
        return work_order_measurements_completed(obj)

    class Meta:
        meta_days = None
        meta_date = timezone.now().date()
        model = Workorder_pichina
        fields = [
            'id',
            'url',
            'name',
            'disposition_name',
            'percent_complete',
            'unit_count',
            'last_action_days',
            'last_action_date',
        ]

