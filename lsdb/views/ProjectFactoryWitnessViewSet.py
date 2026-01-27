from rest_framework import viewsets, status
from rest_framework.response import Response
from lsdb.models import ProjectFactoryWitness, WorkOrder, ReportResult
from lsdb.serializers import ProjectFactoryWitnessSerializer


class ProjectFactoryWitnessViewSet(viewsets.ModelViewSet):
    queryset = ProjectFactoryWitness.objects.all()
    serializer_class = ProjectFactoryWitnessSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        project = serializer.validated_data['project']
        factory_witness_value = serializer.validated_data.get('factory_witness', False)

        # ----------------------------------
        # CREATE or UPDATE (single row only)
        # ----------------------------------
        instance, created = ProjectFactoryWitness.objects.get_or_create(
            project=project,
            defaults={'factory_witness': factory_witness_value}
        )

        if not created:
            instance.factory_witness = factory_witness_value
            instance.save(update_fields=['factory_witness'])

        # ----------------------------------
        # EXISTING SIDE EFFECT LOGIC (UNCHANGED)
        # ----------------------------------
        if instance.factory_witness:
            work_orders = WorkOrder.objects.filter(project=instance.project)
            for work_order in work_orders:
                reports = ReportResult.objects.filter(work_order=work_order)
                for report in reports:
                    if report.data_ready_status == 'Factory witness':
                        report.hex_color = '#4ef542'
                        report.save(update_fields=['hex_color'])

        response_serializer = self.get_serializer(instance)
        headers = self.get_success_headers(response_serializer.data)

        return Response(
            response_serializer.data,
            status=status.HTTP_200_OK if not created else status.HTTP_201_CREATED,
            headers=headers
        )
