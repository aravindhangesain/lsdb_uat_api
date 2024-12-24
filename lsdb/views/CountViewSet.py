from lsdb.models import ProcedureResult
from rest_framework import viewsets
from lsdb.serializers import verifySerializer
# from lsdb.serializers import UnitDataVerificationSerializer
from lsdb.permissions import ConfiguredPermission
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q


class CountViewSet(viewsets.ModelViewSet):
    permission_classes=[ConfiguredPermission]
    serializer_class=verifySerializer

    def retrieve(self, request, pk=None):

        queryset_verified_by = ProcedureResult.objects.filter(unit_id=pk, disposition_id=13)
        verified_by_data = verifySerializer(queryset_verified_by, many=True).data
        verified_by_count = len(verified_by_data)

        queryset_completed = ProcedureResult.objects.filter(Q(unit_id=pk) & (Q(disposition_id=2) & Q(disposition_id=20)))
        completed_data = verifySerializer(queryset_completed, many=True).data
        completed = len(completed_data)

        return Response({
            'verified_by': verified_by_count,
            'completed':completed,
            'total':  verified_by_count,
        })
    
