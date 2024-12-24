from urllib import request
from rest_framework import viewsets
from rest_framework.response import Response
from lsdb.serializers import StepResultNotesSerializer,LocationLogSerializer
from lsdb.models import Asset, StepResultNotes,StepResult,ProcedureResult,Unit,LocationLog
from lsdb.permissions import ConfiguredPermission
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.utils import timezone

class StepResultNotesViewSet(viewsets.ModelViewSet):
    logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
    serializer_class = StepResultNotesSerializer
    # permission_classes = [ConfiguredPermission]
    lookup_field = 'step_result_id'

    def retrieve(self, request, *args, **kwargs):
        step_result_notes = self.get_queryset()
        if not step_result_notes.exists():
            return Response({'detail': 'Not found.'}, status=404)
        serializer = self.get_serializer(step_result_notes, many=True)
        return Response(serializer.data)
    
    def get_queryset(self):
        step_result_id = self.kwargs.get(self.lookup_field)
        return StepResultNotes.objects.filter(step_result_id=step_result_id)

    
    def create(self, request, *args, **kwargs):
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            procedure_result_id = request.data.get('procedure_result')
            step_result_action_id = request.data.get('step_result_action_id')
            step_result_id = request.data.get('step_result')
            asset_id = request.data.get('asset_id')
            datetime = request.data.get('datetime')
            asset = Asset.objects.get(id=asset_id)

            asset = Asset.objects.get(id=asset_id)

            if request.method == "POST":
                test_name=StepResult.objects.get(id=step_result_id)
                if test_name.step_definition.id in [6,32]:

                    
                
    
                    location = asset.location_id

                    procedure_result = ProcedureResult.objects.get(id=procedure_result_id)

                    unit_id = procedure_result.unit_id

                    unit = Unit.objects.get(id=unit_id)

                    unit.location_id = location

                    unit.save()
                    print("updated_location")
                    
                    if not LocationLog.objects.filter(unit_id=unit_id,location_id=location,asset_id=asset_id,is_latest=True).exists():
                        if LocationLog.objects.filter(unit_id=unit_id).exists():
                            LocationLog.objects.filter(unit_id=unit_id).update(is_latest=False)
                            LocationLog.objects.create(location_id=location,unit_id=unit_id,
                                                   datetime=datetime,asset_id=asset_id,is_latest=True,flag=1,username=self.request.user.username)

                        else:
                            LocationLog.objects.create(location_id=location,unit_id=unit_id,
                                                   datetime=datetime,asset_id=asset_id,is_latest=True,flag=1,username=self.request.user.username)

                        

                    
                 
                 

            
            if StepResultNotes.objects.filter(procedure_result_id=procedure_result_id).exists():
                step_result = StepResult.objects.get(id=step_result_id)
                if step_result.name == 'Test End':
                        step_results = StepResultNotes.objects.filter(procedure_result_id=procedure_result_id)
                        step_results.update(is_active=False)
                        serializer.save(username=request.user.username, is_active=True, procedure_result_id=procedure_result_id,asset_id=asset_id,asset_name=asset.name,datetime=datetime)
                        return Response(serializer.data, status=status.HTTP_201_CREATED)
                else :
                    step_results = StepResultNotes.objects.filter(step_result_id=step_result_action_id, is_active=True)
                    if step_results.exists():
                        step_results.update(is_active=False)
                        serializer.save(username=request.user.username, is_active=True, procedure_result_id=procedure_result_id,asset_id=asset_id,asset_name=asset.name,datetime=datetime)
                        return Response({'detail': 'Action done'}, status=status.HTTP_200_OK)
                    elif not StepResultNotes.objects.filter(step_result_id=step_result_action_id).exists():
                        serializer.save(username=request.user.username, is_active=True, procedure_result_id=procedure_result_id,asset_id=asset_id,asset_name=asset.name,datetime=datetime)
                        return Response({'detail': 'Action done'}, status=status.HTTP_200_OK)
                    else:
                        return Response({'detail': 'There is no action available for this step'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                try:
                    step_result = StepResult.objects.get(id=step_result_id)
                    print(step_result.name)
                    if step_result.name != 'Test Resume':
                        serializer.save(username=request.user.username, is_active=True, procedure_result_id=procedure_result_id,asset_id=asset_id,asset_name=asset.name,datetime=datetime)
                        return Response(serializer.data, status=status.HTTP_201_CREATED)
                    
                    else:
                        return Response({'detail': 'There is no action for resume'}, status=status.HTTP_400_BAD_REQUEST)
                except Exception as msg:
                    print(msg)
                    return Response({'detail': 'StepResult does not exist'}, status=status.HTTP_400_BAD_REQUEST)