from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from lsdb.models import ModuleIntakeImages, ModuleIntakeDetails, ReportResult, WorkOrder
from lsdb.serializers import ModuleIntakeImagesSerializer
from azure.storage.blob import BlobServiceClient
import uuid
from django.utils import timezone

class ModuleIntakeImagesViewSet(viewsets.ModelViewSet):
    queryset = ModuleIntakeImages.objects.all()
    serializer_class = ModuleIntakeImagesSerializer

    @action(detail=False, methods=['post'])
    def upload_image(self, request):

        # Check for 'image_path' instead of 'image'
        if 'image_path' not in request.FILES:
            return Response({'status': 'error', 'message': 'No image provided'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            file = request.FILES['image_path']
            file_name = file.name

            # Define the mapping of labels to folder names
            label_to_folder = {
                "Full front side of the module": "full_front_side_of_the_module",
                "Top right corner of the module": "top_right_corner_of_the_module",
                "Full rear side of the module": "full_rear_side_of_the_module",
                "Nameplate": "nameplate",
                "Junction box": "junction_box",
                "Leads": "leads"
            }

            # Extract the label from the request data
            label_name = request.data.get('label_name')
            if not label_name:
                return Response({'status': 'error', 'message': 'Label name not provided'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Determine the folder name based on the label
            folder_name = label_to_folder.get(label_name)
            if not folder_name:
                return Response({'status': 'error', 'message': 'Invalid label name provided'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Azure Blob Storage configuration
            azure_connection_string = 'DefaultEndpointsProtocol=https;AccountName=haveblueazdev;AccountKey=eP954sCH3j2+dbjzXxcAEj6n7vmImhsFvls+7ZU7F4THbQfNC0dULssGdbXdilTpMgaakIvEJv+QxCmz/G4Y+g==;EndpointSuffix=core.windows.net'
            azure_container = 'testmedia1'

            # Validate the connection string
            if not azure_connection_string or 'AccountName=' not in azure_connection_string or 'AccountKey=' not in azure_connection_string:
                return Response({'status': 'error', 'message': 'Connection string is either blank or malformed.'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Upload the file to Azure Blob Storage
            blob_service_client = BlobServiceClient.from_connection_string(azure_connection_string)
            container_client = blob_service_client.get_container_client(azure_container)

            # Create the folder (blob prefix) if it doesn't exist
            blob_name = f"{folder_name}/{uuid.uuid4()}_{file_name}"
            blob_client = container_client.get_blob_client(blob_name)
            blob_client.upload_blob(file)
            
            azure_blob_url = f"https://{blob_service_client.account_name}.blob.core.windows.net/{azure_container}/{blob_name}"

            # Directly get the crate without error checking
            moduleintake_id = request.data.get('moduleintake')
            moduleintake = ModuleIntakeDetails.objects.get(pk=moduleintake_id)
            
            # Extract optional fields from the request data
            intake_date = request.data.get('intake_date')
            received_date = request.data.get('received_date')
            notes = request.data.get('notes')

            uploaded_image = ModuleIntakeImages.objects.create(
                moduleintake=moduleintake,
                label_name=label_name,
                image_path=blob_name,
                status='Active',
                notes=notes
            )

            # Update the steps to step 3 and status to true in ModuleIntakeDetails
            moduleintake.steps = 'step 3'
            moduleintake.is_complete = True
            moduleintake.save()

            # project_id=moduleintake.projects.id
            # workorder=WorkOrder.objects.get(project_id=project_id)

            # if ReportResult.objects.filter(work_order_id=workorder.id,data_ready_status="Module Intake").exists():

            #     valid_intakes=ModuleIntakeDetails.objects.filter(project_id=project_id,bom=workorder.name)
            #     if all("step 3" in intake.steps for intake in valid_intakes):
            #         datetime=timezone.now()

            #         report=ReportResult.objects.filter(work_order_id=workorder.id,data_ready_status="Module Intake").first()

            #         report.hex_color='#4ef542'
            #         report.ready_datetime=datetime

            #         report.save()
                    
            return Response({'status': 'success', 'path': azure_blob_url})
        except Exception as e:
            return Response({'status': 'error', 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)