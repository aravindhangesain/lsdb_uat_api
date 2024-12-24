from django.db import IntegrityError, transaction

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework_tracking.mixins import LoggingMixin
from rest_framework.decorators import action

from lsdb.models import Template
from lsdb.serializers.TemplateSerializer import TemplateSerializer
from lsdb.permissions import ConfiguredPermission, IsAdmin, GroupPermission


class TemplateViewSet(LoggingMixin, viewsets.ModelViewSet):
    """
    API endpoint that allows a Template to be viewed or edited.
    """
    logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
    queryset = Template.objects.all().order_by('id')
    serializer_class = TemplateSerializer
    permission_classes = [ConfiguredPermission]

    def create(self, request, *args, **kwargs):
        data = request.data
        data['author'] = request.user.id

        serializer = self.get_serializer(data=data)

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)
