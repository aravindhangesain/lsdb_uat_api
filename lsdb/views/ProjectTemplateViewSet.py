from rest_framework import viewsets
from lsdb.serializers import ProjectTemplateSerializer
from lsdb.models import ProjectTemplate


class ProjectTemplateViewSet(viewsets.ModelViewSet):

    queryset = ProjectTemplate.objects.all()
    serializer_class = ProjectTemplateSerializer