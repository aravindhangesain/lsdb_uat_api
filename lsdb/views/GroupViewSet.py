import json
from django_filters import rest_framework as filters
from django.db import IntegrityError, transaction
from django.contrib.auth.models import User

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_tracking.mixins import LoggingMixin

from lsdb.serializers import GroupSerializer
from lsdb.models import Group
from lsdb.permissions import ConfiguredPermission


class GroupFilter(filters.FilterSet):
    class Meta:
        model = Group
        fields = [
            'name',
            'group_type',
            'group_type__name',
        ]

class GroupViewSet(LoggingMixin,viewsets.ModelViewSet):
    """
    API endpoint that allows Group to be viewed or edited.
    """
    logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = GroupFilter
    permission_classes = [ConfiguredPermission]

    @transaction.atomic
    @action(detail=True, methods=['get','post'],
        serializer_class=GroupSerializer,
        permission_classes = [ConfiguredPermission],
    )
    def add_users(self, request, pk=None):
        """
        This action will add users to a group.
        POST:
        {
            "id":[ID,ID,ID]
        } to add all User ID to this Group
        """
        self.context={'request':request}
        queryset = Group.objects.get(id=pk)
        if request.method == 'POST':
            params = request.data
            id_list = params.get('id')
            for id in id_list:
                try:
                    queryset.users.add(User.objects.get(pk=id))
                except:
                    # silently fail.
                    pass
            queryset.save()
        return Response(GroupSerializer(queryset, many=False, context=self.context).data)

    @transaction.atomic
    @action(detail=True, methods=['get','post'],
        serializer_class=GroupSerializer,
        permission_classes = [ConfiguredPermission],
    )
    def delete_users(self, request, pk=None):
        """
        This action will remove users from a group.
        POST:
        {
            "id":[ID,ID,ID]
        }
        to remove all User ID to this Group
        """
        self.context={'request':request}
        queryset = Group.objects.get(id=pk)
        if request.method == 'POST':
            params = request.data
            id_list = params.get('id')
            for id in id_list:
                try:
                    queryset.users.remove(User.objects.get(pk=id))
                except:
                    # silently fail.
                    pass
            queryset.save()
        return Response(GroupSerializer(queryset, many=False, context=self.context).data)
