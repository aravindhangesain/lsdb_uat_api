from django.utils import timezone
from rest_framework import viewsets,status
from rest_framework.decorators import action
from lsdb.models import ReportFileTemplate, ReportResult, WorkOrder
from rest_framework.parsers import FileUploadParser
from lsdb.serializers import ReportFileTemplateSerializer
from rest_framework.response import Response
from azure.storage.blob import BlobServiceClient
import os
import re
import string

class ReportFileTemplateViewSet(viewsets.ModelViewSet):
    queryset = ReportFileTemplate.objects.all()
    serializer_class = ReportFileTemplateSerializer

    @action(detail=False, methods=['get'])
    def filter_by_report(self, request):
        report_id = request.query_params.get("report_id")

        if not report_id:
            return Response(
                {"status": "error", "msg": "Missing 'report_id' parameter."},
                status=status.HTTP_400_BAD_REQUEST
            )

        matching_files = ReportFileTemplate.objects.filter(report_id=report_id)

        serializer = self.get_serializer(matching_files, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @staticmethod
    def get_versioned_filename(base_name, extension, existing_names):
        def generate_alpha_suffixes():
            for c in string.ascii_uppercase:
                yield c

        new_name = f"{base_name}{extension}"

        if new_name not in existing_names:
            return new_name

        version_match = re.match(r"^(.*-v\d+)([A-Z]?)$", base_name)

        if version_match:
            base_part = version_match.group(1)  
            existing_suffixes = {
                name for name in existing_names
                if name.startswith(base_part) and name.endswith(extension)
            }

            for suffix in generate_alpha_suffixes():
                candidate = f"{base_part}{suffix}{extension}"
                if candidate not in existing_suffixes:
                    return candidate
        else:
            version = 1
            while True:
                candidate = f"{base_name}-v{version}{extension}"
                if candidate not in existing_names:
                    return candidate
                version += 1


    @action(detail=False, methods=['post'])
    def upload(self, request):
        file_obj = request.FILES.get('file')
        report_id = request.data.get('report')
        workorder_id = request.data.get('workorder')
        user_id = request.data.get('user_id')

        if not file_obj or not report_id or not workorder_id:
            return Response(
                {"status": "error", "msg": "Missing required fields."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            original_filename = file_obj.name  
            base_name, extension = os.path.splitext(original_filename)

            connect_str = 'DefaultEndpointsProtocol=https;AccountName=haveblueazdev;AccountKey=eP954sCH3j2+dbjzXxcAEj6n7vmImhsFvls+7ZU7F4THbQfNC0dULssGdbXdilTpMgaakIvEJv+QxCmz/G4Y+g==;EndpointSuffix=core.windows.net'
            container_name = 'reportmedia'
            blob_service_client = BlobServiceClient.from_connection_string(connect_str)
            container_client = blob_service_client.get_container_client(container_name)

            existing_blob_names = [blob.name for blob in container_client.list_blobs()]

            versioned_filename = self.get_versioned_filename(base_name, extension, existing_blob_names)

            blob_client = container_client.get_blob_client(versioned_filename)
            file_obj.seek(0)
            blob_client.upload_blob(file_obj, overwrite=True)

            report = ReportResult.objects.get(pk=report_id)
            workorder = WorkOrder.objects.get(pk=workorder_id)

            report_file = ReportFileTemplate.objects.create(
                report=report,
                workorder=workorder,
                file=versioned_filename,  
                name=versioned_filename,  
                user_id=user_id,
                datetime=timezone.now()
            )

            serializer = self.get_serializer(report_file)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"status": "error", "msg": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
