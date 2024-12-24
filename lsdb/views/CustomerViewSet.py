import json
from django.db import IntegrityError, transaction
from rest_framework.decorators import action

from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework_tracking.mixins import LoggingMixin
from rest_framework_extensions.mixins import DetailSerializerMixin
from django_filters import rest_framework as filters

from lsdb.serializers import CustomerSerializer
from lsdb.serializers import CustomerDetailSerializer
from lsdb.serializers import NoteSerializer
from lsdb.models import Customer
from lsdb.models import Disposition
from lsdb.models import Note
from lsdb.models import PlexusImport
from lsdb.permissions import ConfiguredPermission, IsAdminOrSelf
from lsdb.utils.NoteUtils import create_note
from django.contrib.auth.models import User


class CustomerFilter(filters.FilterSet):
    class Meta:
        model = Customer
        fields = {
            'name':['exact','icontains'],
            'short_name':['exact','icontains'],
        }

class CustomerViewSet(DetailSerializerMixin, LoggingMixin, viewsets.ModelViewSet):
    """
    API endpoint that allows Customers to be viewed or edited.
    """
    logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    serializer_detail_class = CustomerDetailSerializer
    permission_classes = [ConfiguredPermission]
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = CustomerFilter

    # @transaction.atomic
    # @action(detail=True, methods=['get','post'],
    #     serializer_class = CustomerSerializer,
    # )
    # def add_note(self, request, pk=None):
    #     """
    #     This action is used to add notes to a unit.
    #     POST:
    #     {
    #         "subject": "Unit note subject",
    #         "text": "Unit note text body",
    #         "type":$ID,
    #         "owner": $ID,
    #         "disposition": $ID,
    #         "labels": [$ID1, $ID2...],
    #         "groups": [$ID1, $ID2...],
    #         "tagged_users": [$ID1, $ID2...]
    #     }
    #     """
    #     self.context = {'request':request}
    #     customer = Customer.objects.get(id=pk)
    #     if request.method == "POST":
    #         params = json.loads(request.body)
    #         noteParams = {
    #             "model" : "customer",
    #             "pk" : pk,
    #             "user" : request.user,
    #             "subject" : params.get('subject'),
    #             "text" : params.get('text'),
    #             "note_type" : params.get('type'),
    #         }
    #         if params.get('owner') and params.get('owner') != -1:
    #             noteParams["owner"] = User.objects.get(id=params.get('owner'))
    #         if params.get('disposition') and params.get('disposition')!= -1 :
    #             noteParams["disposition"] =Disposition.objects.get(id=params.get('disposition'))
    #         newNote = create_note(
    #             **noteParams
    #         )
    #         newNote.labels.set(params.get('labels'))
    #         newNote.groups.set(params.get('groups'))
    #         newNote.tagged_users.set(params.get('tagged_users'))
    #         newNote.save()
    #         serializer = NoteSerializer(newNote,many=False, context=self.context)
    #     else:
    #         serializer = NoteSerializer([], many=True, context=self.context)
    #     return Response(serializer.data)

    @action(detail=True, methods=['get',],
        serializer_class=NoteSerializer,
    )
    def notes(self, request, pk=None):
        customer = Customer.objects.get(id=pk)
        self.context = {'request':request}
        serializer = NoteSerializer(customer.notes.all(),many=True, context=self.context)
        return Response(serializer.data)

    @transaction.atomic
    @action(detail=True, methods=['get','post'],
        serializer_class = CustomerSerializer,
        permission_classes = [IsAdminOrSelf,ConfiguredPermission,]
    )
    def merge(self, request, pk=None):
        """
        This action is used to add another customer object's data to this one .
        POST:
        {
            "id": ID
        }
        DANGER DANGER DANGER DELETES OBJECTS
        """
        self.context = {'request':request}
        customer = Customer.objects.get(id=pk)
        if request.method == "POST":
            params = json.loads(request.body)
            obsolete = Customer.objects.get(id=params.get('id'))
            for note in obsolete.notes.all():
                customer.notes.add(note)
                obsolete.notes.delete(note)
            for unit_type in obsolete.unittype_set.all():
                unit_type.manufacturer = customer
                unit_type.save()
            for crate in obsolete.crate_set.all():
                crate.shipped_by = customer
                crate.save()
            for project in obsolete.project_set.all():
                project.customer = customer
                project.save()
            for oid in PlexusImport.objects.filter(lsdb_id=params.get('id'), lsdb_model='customer'):
                oid.lsdb_id = customer.id
                oid.save()
            customer.save()
            obsolete.delete()
        serializer = CustomerSerializer(customer,many=False, context=self.context)
        return Response(serializer.data)
