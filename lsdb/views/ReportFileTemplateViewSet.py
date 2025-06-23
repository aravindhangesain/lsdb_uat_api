from django.utils import timezone
from rest_framework import viewsets,status
from rest_framework.decorators import action
from lsdb.models import ReportFileTemplate, ReportResult, WorkOrder
from rest_framework.parsers import FileUploadParser
from lsdb.serializers import ReportFileTemplateSerializer
from django.http import HttpResponse
from rest_framework.response import Response
from azure.storage.blob import BlobServiceClient
from docx import Document
import magic

class ReportFileTemplateViewSet(viewsets.ModelViewSet):
    queryset = ReportFileTemplate.objects.all()
    serializer_class = ReportFileTemplateSerializer
    parser_class = (FileUploadParser,)

    @action(detail=False, methods=['post'])
    def upload(self, request):
        file_obj = request.FILES.get('file')
        report_id = request.data.get('report')
        workorder_id = request.data.get('workorder')
        user_id = request.data.get('user_id')
        if not file_obj or not report_id or not workorder_id:
            return Response({"status": "error", "msg": "Missing required fields."},status=status.HTTP_400_BAD_REQUEST)
        try:
            document = Document(file_obj)
            name = document.paragraphs[0].text.strip()
            file_obj.seek(0)
            connect_str = 'DefaultEndpointsProtocol=https;AccountName=haveblueazdev;AccountKey=eP954sCH3j2+dbjzXxcAEj6n7vmImhsFvls+7ZU7F4THbQfNC0dULssGdbXdilTpMgaakIvEJv+QxCmz/G4Y+g==;EndpointSuffix=core.windows.net'
            container_name = 'reportmedia'
            blob_service_client = BlobServiceClient.from_connection_string(connect_str)
            blob_client = blob_service_client.get_blob_client(container=container_name, blob=file_obj.name)
            blob_client.upload_blob(file_obj, overwrite=True)
            report = ReportResult.objects.get(pk=report_id)
            workorder = WorkOrder.objects.get(pk=workorder_id)
            azure_path = file_obj.name
            report_file = ReportFileTemplate.objects.create(
                report=report,
                workorder=workorder,
                file=azure_path,
                name=name,
                user_id=user_id,
                datetime=timezone.now()
            )
            serializer = self.get_serializer(report_file)
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"status": "error", "msg": str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
