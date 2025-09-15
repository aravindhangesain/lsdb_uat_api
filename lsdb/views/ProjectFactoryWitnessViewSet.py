from rest_framework import viewsets,status
from lsdb.models import *
from lsdb.serializers import *
from rest_framework.response import Response


class ProjectFactoryWitnessViewSet(viewsets.ModelViewSet):

    queryset = ProjectFactoryWitness.objects.all()
    serializer_class = ProjectFactoryWitnessSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        instance = serializer.save()

        if instance.factory_witness:
            work_orders = WorkOrder.objects.filter(project=instance.project)
            for work_order in work_orders:
                reports = ReportResult.objects.filter(work_order=work_order)
                for report in reports:
                    if report.data_ready_status == 'Factory witness':
                        report.hex_color = '#4ef542'
                        report.save()
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

        


    