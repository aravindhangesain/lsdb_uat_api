from rest_framework import viewsets
from lsdb.models import TemplateDetails
from lsdb.serializers import TemplateDetailsSerializer

class TemplateDetailsViewSet(viewsets.ModelViewSet):

    queryset=TemplateDetails.objects.all()
    serializer_class=TemplateDetailsSerializer