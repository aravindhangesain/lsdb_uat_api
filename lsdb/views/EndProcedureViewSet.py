from rest_framework import viewsets
from lsdb.models import Unit,ProcedureResult,Disposition,StepResult,Asset,MeasurementResult,StepResultNotes
from lsdb.serializers import UnitSerializer
from rest_framework.response import Response
from rest_framework.decorators import action
from django.contrib.auth.models import User
from datetime import datetime





class EndProcedureViewSet(viewsets.ModelViewSet):

    queryset=Unit.objects.all()
    serializer_class=UnitSerializer

    @action(detail=False, methods=['post'])
    def end_procedure(self, request):
        serial_number=request.data.get('serial_number')
        asset_name=request.data.get('asset_name')
        username=request.data.get('username')
        current_datetime = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S+00')


        unit=Unit.objects.filter(serial_number=serial_number).first()
        unit_id=unit.id

        disposition = Disposition.objects.get(name__iexact='in progress')
        procedure=ProcedureResult.objects.filter(
            unit_id=unit_id,
            disposition=disposition,
            stepresult__disposition__isnull=False,
            stepresult__name__iexact="test start",
            group__name__iexact='stressors'
        ).exclude(test_sequence_definition__group__name__iexact="control").distinct().order_by('linear_execution_group').first()
        if procedure is None:
            print("no such procedure")

        procedure_result_id=procedure.id
        ProcedureResult.objects.filter(id=procedure_result_id).update(disposition=20,end_datetime=current_datetime)

        asset=Asset.objects.filter(name=asset_name).first()
        user=User.objects.filter(username=username).first()
        step=StepResult.objects.filter(procedure_result_id=procedure_result_id,name='Test End').first()
        if step:
            StepResult.objects.filter(procedure_result_id=procedure_result_id,name='Test End').update(disposition=20,start_datetime=current_datetime)

            # step.disposition = 20
            # step.start_datetime = datetime
            # step.save()

            MeasurementResult.objects.filter(step_result_id=step.id, name='End Time').update(
                asset_id=asset.id, date_time=current_datetime, result_datetime=current_datetime, start_datetime=current_datetime, disposition=20, user_id=user.id
            )
        
            StepResultNotes.objects.create(step_result_id=step.id,username=username,datetime=current_datetime,procedure_result_id=procedure_result_id,is_active=True,asset_id=asset.id,asset_name=asset.name)
            return Response(["success: Stress Exit successfully completed"])
        else:
            return Response(["error"])