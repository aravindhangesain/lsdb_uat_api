from rest_framework import viewsets
from lsdb.models import NewCrateIntake
from lsdb.serializers import NewCrateIntakeSerializer
from django_filters import rest_framework as filters
# from lsdb.permissions import ConfiguredPermission
from datetime import datetime

class NewCrateIntakeFilter(filters.FilterSet):
    class Meta:
        model = NewCrateIntake
        fields = [
            
            'customer',
            'manufacturer',
            'project',
            'crate_intake_date'

        ]

class NewCrateIntakeViewSet(viewsets.ModelViewSet):
    
    logging_methods = ['GET','POST', 'PATCH', 'DELETE']
    queryset = NewCrateIntake.objects.all()
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = NewCrateIntakeFilter
    serializer_class = NewCrateIntakeSerializer
    # permission_classes = [ConfiguredPermission]
    lookup_field= "project"

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user.username)
        
        
