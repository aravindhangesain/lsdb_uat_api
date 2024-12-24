from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from lsdb.models import CrateIntakeImages, NewCrateIntake
from lsdb.serializers import CrateIntakeImagesSerializer
from azure.storage.blob import BlobServiceClient
import uuid

class CrateIntakeImagesViewSet(viewsets.ModelViewSet):
    logging_methods = ['GET','POST']
    queryset = CrateIntakeImages.objects.all()
    serializer_class = CrateIntakeImagesSerializer

    @action(detail=False, methods=['post'])
    def upload_image(self, request):
        if 'image_path' not in request.FILES:
            return Response({'status': 'error', 'message': 'No image provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            file = request.FILES['image_path']
            file_name = file.name

            label_to_folder = {
                "Crates inside truck": "crates_inside_truck",
                "Each crate on the forklift": "each_crate_on_the_forklift",
                "All 4 sides of each crate when fully offloaded": "all_4_sides_of_each_crate",
                "All visible damage": "all_visible_damage",
                "Shipping labels": "shipping_labels"
            }

            label_name = request.data.get('label_name')
            if not label_name:
                return Response({'status': 'error', 'message': 'Label name not provided'}, status=status.HTTP_400_BAD_REQUEST)

            folder_name = label_to_folder.get(label_name)
            if not folder_name:
                return Response({'status': 'error', 'message': 'Invalid label name provided'}, status=status.HTTP_400_BAD_REQUEST)

            azure_connection_string = 'DefaultEndpointsProtocol=https;AccountName=haveblueazdev;AccountKey=eP954sCH3j2+dbjzXxcAEj6n7vmImhsFvls+7ZU7F4THbQfNC0dULssGdbXdilTpMgaakIvEJv+QxCmz/G4Y+g==;EndpointSuffix=core.windows.net'
            azure_container = 'testmedia1'

            if not azure_connection_string or 'AccountName=' not in azure_connection_string or 'AccountKey=' not in azure_connection_string:
                return Response({'status': 'error', 'message': 'Connection string is either blank or malformed.'}, status=status.HTTP_400_BAD_REQUEST)

            blob_service_client = BlobServiceClient.from_connection_string(azure_connection_string)
            container_client = blob_service_client.get_container_client(azure_container)

            blob_name = f"{folder_name}/{uuid.uuid4()}_{file_name}"
            blob_client = container_client.get_blob_client(blob_name)
            blob_client.upload_blob(file)

            azure_blob_url = f"https://{blob_service_client.account_name}.blob.core.windows.net/{azure_container}/{blob_name}"

            crate_id = request.data.get('newcrateintake')
            crate = NewCrateIntake.objects.get(pk=crate_id)
            notes = request.data.get('notes')

            uploaded_image = CrateIntakeImages.objects.create(
                newcrateintake=crate,
                label_name=label_name,
                image_path=blob_name,
                status='Active',
                notes=notes
            )

            return Response({'status': 'success', 'path': azure_blob_url})

        except Exception as e:
            return Response({'status': 'error', 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
