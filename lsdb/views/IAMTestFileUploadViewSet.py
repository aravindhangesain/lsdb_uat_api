from rest_framework import viewsets, status
from rest_framework.response import Response
from azure.storage.blob import BlobServiceClient, ContentSettings
from lsdb.models import IAMTestFileUpload, Unit
from lsdb.serializers import IAMTestFileUploadSerializer
from datetime import datetime

class IAMTestFileUploadViewSet(viewsets.ModelViewSet):
    logging_methods = ['GET']
    queryset = IAMTestFileUpload.objects.all()
    serializer_class = IAMTestFileUploadSerializer

    AZURE_STORAGE_CONNECTION_STRING = 'DefaultEndpointsProtocol=https;AccountName=haveblueazdev;AccountKey=eP954sCH3j2+dbjzXxcAEj6n7vmImhsFvls+7ZU7F4THbQfNC0dULssGdbXdilTpMgaakIvEJv+QxCmz/G4Y+g==;EndpointSuffix=core.windows.net'
    AZURE_CONTAINER_NAME = 'testmedia1'

    def create(self, request, *args, **kwargs):
        if 'file_path' not in request.FILES:
            return Response({'detail': 'No file provided.'}, status=status.HTTP_400_BAD_REQUEST)

        if 'serial_number' not in request.data:
            return Response({'detail': 'No serial number provided.'}, status=status.HTTP_400_BAD_REQUEST)

        serial_number = request.data['serial_number']

        try:
            # Check if the serial number exists in Unit
            unit = Unit.objects.get(serial_number=serial_number)
            file_obj = request.FILES['file_path']
            
            # Upload file to Azure Blob Storage
            blob_service_client = BlobServiceClient.from_connection_string(self.AZURE_STORAGE_CONNECTION_STRING)
            blob_client = blob_service_client.get_blob_client(container=self.AZURE_CONTAINER_NAME, blob=file_obj.name)
            blob_client.upload_blob(file_obj, content_settings=ContentSettings(content_type=file_obj.content_type))

            # Save file information in the database
            iam_test_file_upload = IAMTestFileUpload.objects.create(
                file_path=file_obj.name,
                serial_number=unit,
                uploaded_date=datetime.now().strftime('%Y-%m-%d')
            )

            serializer = self.get_serializer(iam_test_file_upload)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Unit.DoesNotExist:
            return Response({'detail': 'Unit with the provided serial number does not exist.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)
