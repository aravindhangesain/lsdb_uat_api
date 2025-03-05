from rest_framework import viewsets
from lsdb.models import ReportTypeDefinition
from lsdb.serializers import ReportTypeDefinitionSerializer
from rest_framework.response import Response
from django.db import IntegrityError, transaction
from rest_framework.decorators import action



class ReportTypeDefinitionViewSet(viewsets.ModelViewSet):
    queryset = ReportTypeDefinition.objects.all()
    serializer_class = ReportTypeDefinitionSerializer

    # @transaction.atomic()
    # @action(detail=False, methods=['get', 'post'],)
    # def bulk_report_creation(self, request):
        
    #     report_names=request.data.get('report_names',[])
    #     for name in report_names:
    #         ReportTypeDefinition.objects.create(name=name,disposition_id=16,group_id=4,version=1,linear_execution_order=1)
    #     return Response("created")
