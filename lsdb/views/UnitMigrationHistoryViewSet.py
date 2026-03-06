from rest_framework import viewsets
from lsdb.models import *
from lsdb.serializers import *

class UnitMigrationHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = UnitMigrationHistory.objects.all().order_by('-migration_date')
    serializer_class = UnitMigrationHistorySerializer