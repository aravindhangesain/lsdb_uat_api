from rest_framework import viewsets,status
from lsdb.models import ModuleIntake,ModuleIntakeDetails,ModuleIntakeImages
from lsdb.serializers import ModuleIntakeImagesSerializer,ModuleUpdateSerializer
from rest_framework.response import Response
from rest_framework.decorators import action
from azure.storage.blob import BlobServiceClient
import uuid

class ModuleUpdateViewSet(viewsets.ModelViewSet):
    queryset=ModuleIntakeImages.objects.all()
    serializer_class=ModuleUpdateSerializer

    @action(detail=False, methods=['put'])
    def update_image(self, request):
        moduleintake_id = request.data.get('moduleintake')
        moduleintakeimage_id = request.data.get('id')
        notes = request.data.get('notes')
        label_name = request.data.get('label_name')

        if moduleintake_id and 'moduleintake_date' and 'received_date' in request.data:
            moduleintake_date = request.data.get('moduleintake_date')
            received_date = request.data.get('received_date')
            try:
                ModuleIntakeDetails.objects.filter(id=moduleintake_id).update(intake_date=moduleintake_date,received_date=received_date)
                return Response({'status': 'success', 'message': 'intake date and received date updated successfully'})
            except Exception as e:
                return Response({'status': 'error', 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        elif moduleintake_id and 'moduleintake_date' in request.data:
            moduleintake_date = request.data.get('moduleintake_date')
            try:
                ModuleIntakeDetails.objects.filter(id=moduleintake_id).update(intake_date=moduleintake_date)
                return Response({'status': 'success', 'message': 'intake date updated successfully'})
            except Exception as e:
                return Response({'status': 'error', 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        elif moduleintake_id and 'received_date' in request.data:
            received_date = request.data.get('received_date')
            try:
                ModuleIntakeDetails.objects.filter(id=moduleintake_id).update(received_date=received_date)
                return Response({'status': 'success', 'message': 'received date updated successfully'})
            except Exception as e:
                return Response({'status': 'error', 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        elif moduleintakeimage_id and moduleintake_id:
            try:
                # Assuming these are commented for a reason, and you handle the file and blob name somewhere else
                file = request.FILES['image_path']
                file_name = file.name
                label_to_folder = {
                "Full front side of the module": "full_front_side_of_the_module",
                "Top right corner of the module": "top_right_corner_of_the_module",
                "Full rear side of the module": "full_rear_side_of_the_module",
                "Nameplate": "nameplate",
                "Junction box": "junction_box",
                "Leads": "leads"
            }
                folder_name = label_to_folder.get(label_name)
                if not folder_name:
                    return Response({'status': 'error', 'message': 'Invalid label name provided'}, status=status.HTTP_400_BAD_REQUEST)
                
                azure_connection_string = 'DefaultEndpointsProtocol=https;AccountName=haveblueazdev;AccountKey=eP954sCH3j2+dbjzXxcAEj6n7vmImhsFvls+7ZU7F4THbQfNC0dULssGdbXdilTpMgaakIvEJv+QxCmz/G4Y+g==;EndpointSuffix=core.windows.net'
                azure_container = 'testmedia1'
                blob_service_client = BlobServiceClient.from_connection_string(azure_connection_string)
                container_client = blob_service_client.get_container_client(azure_container)
                blob_name = f"{folder_name}/{uuid.uuid4()}_{file_name}"
                blob_client = container_client.get_blob_client(blob_name)
                blob_client.upload_blob(file, overwrite=True)
                azure_blob_url = f"https://{blob_service_client.account_name}.blob.core.windows.net/{azure_container}/{blob_name}"
                # Update CrateIntakeImages instance
                image_instance = ModuleIntakeImages.objects.filter(moduleintake_id=moduleintake_id, id=moduleintakeimage_id).first()
                if image_instance:
                    image_instance.label_name = label_name
                    image_instance.image_path = blob_name
                    image_instance.status = 'Active'
                    # image_instance.notes = notes
                    image_instance.save()
                    return Response({'status': 'success', 'path': notes})
                else:
                    return Response({'status': 'error', 'message': f'Image with newcrateintake_id {moduleintake_id} does not exist'}, status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                return Response({'status': 'error', 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        # Default response if none of the conditions are met
        return Response({'status': 'error', 'message': 'Invalid request data'}, status=status.HTTP_400_BAD_REQUEST)
