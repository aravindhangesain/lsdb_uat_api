from rest_framework import viewsets
from lsdb.models import ProcedureResult_pichina
from lsdb.serializers import Procedureresult_pichinaSerializer
from lsdb.permissions import ConfiguredPermission



class ProcedureResult_pichinaViewSet(viewsets.ModelViewSet):
    logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
    queryset = ProcedureResult_pichina.objects.all()
    serializer_class = Procedureresult_pichinaSerializer
    permission_classes = [ConfiguredPermission]

    