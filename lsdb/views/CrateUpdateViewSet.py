from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from lsdb.models import CrateIntakeImages, NewCrateIntake
from lsdb.serializers import CrateUpdateSerializer
from azure.storage.blob import BlobServiceClient
import uuid


class CrateUpdateViewSet(viewsets.ModelViewSet):
    queryset = CrateIntakeImages.objects.all()
    serializer_class = CrateUpdateSerializer

    @action(detail=False, methods=['put'])
    def update_image(self, request):
        newcrateintake = request.data.get('newcrateintake')
        label_name = request.data.get('label_name')
        notes = request.data.get('notes')
        crateintakeimage_id = request.data.get('id')

        # Handle crate intake date update
        if newcrateintake and 'crate_intake_date' in request.data:
            crate_intake_date = request.data.get('crate_intake_date')
            try:
                NewCrateIntake.objects.filter(id=newcrateintake).update(crate_intake_date=crate_intake_date)
                return Response({'status': 'success', 'message': 'Crate intake date updated successfully'})
            except Exception as e:
                return Response({'status': 'error', 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Handle image upload and update
        elif crateintakeimage_id and newcrateintake:
            try:
                # Assuming these are commented for a reason, and you handle the file and blob name somewhere else
                file = request.FILES['image_path']
                file_name = file.name

                label_to_folder = {
                    "Crates inside truck": "crates_inside_truck",
                    "Each crate on the forklift": "each_crate_on_the_forklift",
                    "All 4 sides of each crate when fully offloaded": "all_4_sides_of_each_crate",
                    "All visible damage": "all_visible_damage",
                    "Shipping labels": "shipping_labels"
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
                image_instance = CrateIntakeImages.objects.filter(newcrateintake_id=newcrateintake, id=crateintakeimage_id).first()
                if image_instance:
                    image_instance.label_name = label_name
                    image_instance.image_path = blob_name
                    image_instance.status = 'Active'
                    # image_instance.notes = notes
                    image_instance.save()

                    return Response({'status': 'success', 'path': notes})
                else:
                    return Response({'status': 'error', 'message': f'Image with newcrateintake_id {newcrateintake} does not exist'}, status=status.HTTP_404_NOT_FOUND)

            except Exception as e:
                return Response({'status': 'error', 'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Default response if none of the conditions are met
        return Response({'status': 'error', 'message': 'Invalid request data'}, status=status.HTTP_400_BAD_REQUEST)
