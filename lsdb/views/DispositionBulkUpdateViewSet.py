from rest_framework import viewsets
from rest_framework.response import Response
from lsdb.models import Project, WorkOrder, Unit, TestSequenceDefinition
from lsdb.serializers import DispositionBulkUpdateSerializer

class DispositionBulkUpdateViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = DispositionBulkUpdateSerializer
    lookup_field = 'number'

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        if 'disposition' in serializer.validated_data:
            new_disposition = serializer.validated_data['disposition']
            if new_disposition != instance.disposition:

                # Update disposition ID of the project
                instance.disposition = new_disposition
                instance.save()

                # Update disposition ID of work orders associated with the project
                work_orders = WorkOrder.objects.filter(project=instance)
                for work_order in work_orders:
                    work_order.disposition = new_disposition
                    work_order.save()

                    units = Unit.objects.filter(workorder=work_order)
                    for unit in units:
                        unit.disposition = new_disposition
                        unit.save()

                    # Update test sequence definition of units
                    test_sequence_defs = TestSequenceDefinition.objects.filter(
                        testsequenceexecutiondata__work_order=work_order
                    )
                    for test_sequence_def in test_sequence_defs:
                        if test_sequence_def.disposition_id not in [3, 8]:
                            test_sequence_def.disposition = new_disposition
                            test_sequence_def.save()
                            
        return Response(serializer.data)