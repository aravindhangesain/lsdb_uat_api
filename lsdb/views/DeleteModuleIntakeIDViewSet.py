from django.db import connection
from rest_framework import status, viewsets
from rest_framework.response import Response
from lsdb.models import ModuleIntakeDetails, ScannedPannels
from rest_framework.decorators import action
from lsdb.serializers import DeleteModuleIntakeDetailsSerializer


class DeleteModuleIntakeIDViewSet(viewsets.ModelViewSet):
    queryset = ModuleIntakeDetails.objects.all()
    serializer_class = DeleteModuleIntakeDetailsSerializer

    @action(detail=False, methods=["post"])
    def custom_delete(self, request, pk=None):
        # Retrieve `id` from the request data
        item_id = request.data.get("id")
        if not item_id:
            return Response(
                {"error": "Missing 'id' in request data"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Step 1: Retrieve the serial numbers from ScannedPannels before deleting them
            panel_ids = ScannedPannels.objects.filter(module_intake_id=item_id)
            serial_numbers = [panel.serial_number for panel in panel_ids]

            # Step 2: Delete related rows from all tables
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM lsdb_moduleintakeimages WHERE moduleintake_id = %s",[item_id],)
                cursor.execute("DELETE FROM lsdb_scannedpannels WHERE module_intake_id = %s",[item_id],)
                cursor.execute("DELETE FROM lsdb_moduleintakedetails WHERE id = %s", [item_id])

                for serial_number in serial_numbers:
                    cursor.execute(
                        "DELETE FROM lsdb_unit WHERE serial_number = %s",
                        [serial_number],
                    )

            return Response(
                {"message": "Item deleted successfully"},
                status=status.HTTP_204_NO_CONTENT,
            )
        except Exception as e:
            return Response(
                {"error": f"An unexpected error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
