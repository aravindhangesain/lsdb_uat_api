from rest_framework import viewsets, status

from lsdb.models import FinalProcedure
from lsdb.serializers import FinalProcedureSerializer


class FinalProcedureViewSet(viewsets.ModelViewSet):

    queryset=FinalProcedure.objects.all()
    serializer_class=FinalProcedureSerializer