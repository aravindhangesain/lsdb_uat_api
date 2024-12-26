from rest_framework import status
from rest_framework.response import Response
from rest_framework import viewsets
from lsdb.models import ModuleIntakeDetails
from lsdb.serializers import DeleteModuleIntakeDetailsSerializer

class DeleteModuleIntakeIDViewSet(viewsets.ModelViewSet):
    queryset = ModuleIntakeDetails.objects.all()
    serializer_class = DeleteModuleIntakeDetailsSerializer

    def destroy(self, request, pk=None):
        item_id = request.data.get('id')
        try:
            ModuleIntakeDetails.objects.filter(id=item_id).delete()
            return Response({"message": "Item deleted successfully"})
        except:
            return Response({"message": "Item not found"}, status=status.HTTP_404_NOT_FOUND)