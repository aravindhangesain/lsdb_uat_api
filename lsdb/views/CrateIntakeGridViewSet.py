from rest_framework import viewsets
from lsdb.models import NewCrateIntake
from lsdb.serializers import CrateIntakeGridSerializer
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

class CrateIntakeGridViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = NewCrateIntake.objects.all().order_by('-crate_intake_date')
    serializer_class = CrateIntakeGridSerializer
    # pagination_class = MyCustomPagination


