from rest_framework import viewsets
from lsdb.serializers import GetModuleDetailsSerializer
from lsdb.models import UnitType
from rest_framework.response import Response

class GetModuleDetailsViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows ModuleProperty to be viewed or edited.
    """
    logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
    serializer_class = GetModuleDetailsSerializer

    def get_queryset(self):
        module_type = self.request.query_params.get('module_type')
        if module_type:
            var = UnitType.objects.filter(model=module_type)
            if var.exists():
                return var  # or return var.first().mode if you need a specific field
        return UnitType.objects.none()
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        if queryset.exists():
            serializer = self.get_serializer(queryset.first())
            return Response(serializer.data)
        return Response({})