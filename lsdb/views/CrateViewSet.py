import json
from django.db import IntegrityError, transaction

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_tracking.mixins import LoggingMixin

from lsdb.models import AzureFile
from lsdb.models import Crate
from lsdb.models import Project
from lsdb.models import Note
from lsdb.models import Disposition
from lsdb.models import DispositionCode

from lsdb.serializers import AzureFileSerializer
from lsdb.serializers import CrateSerializer
from lsdb.serializers import NoteSerializer
from lsdb.serializers import DispositionCodeListSerializer
from lsdb.permissions import ConfiguredPermission

from django.contrib.auth.models import User
# from lsdb.utils.NoteUtils import create_note

class CrateViewSet(LoggingMixin, viewsets.ModelViewSet):
    """
    API endpoint that allows Crates to be viewed or edited.
    """
    logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
    # because this is filtered, I need an unfiltered "all" action below
    queryset = Crate.objects.filter(disposition__name__iexact='available')
    serializer_class = CrateSerializer
    permission_classes = [ConfiguredPermission]

    @action(detail=False, methods=['get',],
        serializer_class=DispositionCodeListSerializer,
    )
    def dispositions(self, request, pk=None):
        self.context={'request':request}
        serializer = DispositionCodeListSerializer(DispositionCode.objects.get(
            name='crates'),
            many=False,
            context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get',],
        serializer_class=CrateSerializer,
    )
    def all(self, request, pk=None):
        self.context={'request':request}
        return Response(
            self.serializer_class(
                Crate.objects.all(),
                many=True,
                context={'request': request}
                ).data
            )

        serializer = DispositionCodeListSerializer(DispositionCode.objects.get(
            name='crates'),
            many=False,
            context={'request': request})

    # TODO: NEED TO ADD add_workorder here
    @action(detail=True, methods=['get',],
        serializer_class=NoteSerializer,
    )
    def notes(self, request, pk=None):
        crate=Crate.objects.get(id=pk)
        self.context = {'request':request}
        type = request.query_params.get('type')
        if type:
            queryset=crate.notes.filter(note_type=type)
        else:
            queryset=crate.notes.all()
        serializer = NoteSerializer(queryset,many=True, context=self.context)
        return Response(serializer.data)


    # @transaction.atomic
    # @action(detail=True, methods=['get','post'],
    #     permission_classes=(ConfiguredPermission,),
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
    #     crate = Crate.objects.get(id=pk)
    #     if request.method == "POST":
    #         params = json.loads(request.body)
    #         noteParams = {
    #             "model" : "crate",
    #             "pk" : pk,
    #             "user" : request.user,
    #             "subject" : params.get('subject'),
    #             "text" : params.get('text'),
    #             "note_type" : params.get('type'),
    #             "parent_note" : ( Note.objects.get(id=params.get('note')) if params.get('note') else None),
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

    @action(detail=True, methods=['get','post'],
        serializer_class=CrateSerializer,
    )
    def link_files(self, request, pk=None):
        """
        This action will link an existing AzureFile to this unit.
        POST: {"id":1} to link azurfefile id=1 to this unit
        """
        self.context={'request':request}
        queryset = Crate.objects.get(id=pk)
        if request.method == 'POST':
            params = json.loads(request.body)
            file_id = params.get('id')
            if file_id:
                attachment = AzureFile.objects.get(id=int(file_id))
                queryset.crate_images.add(attachment)
                queryset.save()
        serializer = CrateSerializer(queryset, many=False, context=self.context)
        return Response(serializer.data)

    @action(detail=False, methods=['get','post'],
        serializer_class=CrateSerializer,
    )
    def mark_empty(self, request, pk=None):
        """
        This action will mark a crate empty. --> disposition = `Completed`
        {"id":$ID}
        returns crate object on success.
        """
        self.context={'request':request}
        errors =[]
        queryset = {}
        if request.method == 'POST':
            params = json.loads(request.body)
            crate_id = params.get('id')
            if crate_id:
                try:
                    disposition = Disposition.objects.get(name__iexact = 'completed')
                except:
                    errors.append(
                        "Error: 'Completed' disposition configured incorrectly. Call Engineering!"
                    )
                    return Response(errors)
                try:
                    crate = Crate.objects.get(id=int(crate_id))
                except:
                    errors.append(
                        "Error: Crate with ID {} not found".format(crate_id)
                    )
                    return Response(errors)
                crate.disposition = disposition
                crate.save()
                serializer = CrateSerializer(crate, many=False, context=self.context)
                # KLUGE: Still not fond of this flow pattern of return in the middle of an ~if~
                return Response(serializer.data)
        else:
            return Response({})

    @action(detail=True, methods=['get', 'post'],
        serializer_class=CrateSerializer,
    )
    def attach_project(self, request, pk=None):
        self.context={'request':request}
        errors = []
        queryset = Crate.objects.get(id=pk)
        if request.method == 'POST':
            params = json.loads(request.body)
            project_id = params.get('project_id')
            if project_id:
                try:
                    project = Project.objects.get(id = project_id)
                except:
                    errors.append(
                        "Error: Project does not exist. Please contact engineering."
                    )
                    return Response(errors)
                queryset.project = project
                queryset.save()
                serializer = CrateSerializer(queryset, many=False, context=self.context)
                return Response(serializer.data)
        else:
            return Response(CrateSerializer(queryset, many=False, context=self.context).data)
