import json
import pandas as pd
from django.db import IntegrityError, transaction
from django.db.models import Q, Max
from django_filters import rest_framework as filters

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_tracking.mixins import LoggingMixin

from lsdb.models import Asset
from lsdb.models import Disposition
from lsdb.models import MeasurementDefinition
from lsdb.models import ProcedureDefinition
from lsdb.models import Unit

from lsdb.serializers import AssetSerializer
from lsdb.serializers import NoteSerializer
from lsdb.serializers import MeasurementDefinitionSerializer
from lsdb.serializers import ProcedureDefinitionSerializer
from lsdb.permissions import ConfiguredPermission
# from lsdb.utils.NoteUtils import create_note

class AssetFilter(filters.FilterSet):
    last_action_min = filters.DateFilter(lookup_expr='gte', field_name='last_action_datetime')
    last_action_max = filters.DateFilter(lookup_expr='lte', field_name='last_action_datetime')

    class Meta:
        model = Asset
        fields = [
            'name',
            'description',
            'location',
            'last_action_datetime',
            'asset_types',
            'disposition',
            'last_action_min',
            'last_action_max',
        ]

class AssetViewSet(LoggingMixin, viewsets.ModelViewSet):
    """
    API endpoint that allows Asset to be viewed or edited.
    Filters:
    ?name= ,
    'description',
    'location',
    'last_action_datetime',
    'asset_type',
    'disposition',
    'last_action_min',
    'last_action_max',
    """
    logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
    queryset = Asset.objects.all()
    serializer_class = AssetSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = AssetFilter
    permission_classes = [ConfiguredPermission]

    # @transaction.atomic
    # @action(detail=True, methods=['get','post'],
    #     permission_classes=(ConfiguredPermission,),
    # )
    # def add_note(self, request, pk=None):
    #     """
    #     This action is used to add notes to an asset.
    #     POST:
    #     {
    #         "subject": "Asset note subject",
    #         "text": "Asset note text body",
    #         "type":$ID,
    #         "owner": $ID,
    #         "disposition": $ID,
    #         "labels": [$ID1, $ID2...],
    #         "groups": [$ID1, $ID2...],
    #         "tagged_users": [$ID1, $ID2...]
    #     }
    #     """
    #     self.context = {'request':request}
    #     unit = Unit.objects.get(id=pk)
    #     if request.method == "POST":
    #         params = json.loads(request.body)
    #         noteParams = {
    #             "model" : "asset",
    #             "pk" : pk,
    #             "user" : request.user,
    #             "subject" : params.get('subject'),
    #             "text" : params.get('text'),
    #             "note_type" : params.get('type'),
    #             }
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
    #     serializer = NoteSerializer(newNote,many=False, context=self.context)
    #     return Response(serializer.data)

    @action(detail=True, methods=['get',],
        serializer_class=MeasurementDefinitionSerializer,
    )
    def measurements(self, request, pk=None):
        """
        Returns all measurements that this asset can perform
        """
        self.context={'request':request}
        asset = Asset.objects.get(id=pk)
        measurements = MeasurementDefinition.objects.filter(step_definition__proceduredefinition__asset_types__in=asset.asset_types.all())
        serializer = self.serializer_class(measurements.distinct(), many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['get',],
        serializer_class=NoteSerializer,
    )
    def notes(self, request, pk=None):
        asset=Asset.objects.get(id=pk)
        self.context = {'request':request}
        serializer = NoteSerializer(asset.notes.all(),many=True, context=self.context)
        return Response(serializer.data)

    @action(detail=True, methods=['get',],
        serializer_class=ProcedureDefinitionSerializer,
    )
    def procedures(self, request, pk=None):
        """
        Returns all procedures that this asset can perform
        """
        self.context={'request':request}
        asset = Asset.objects.get(id=pk)
        procedures = ProcedureDefinition.objects.filter(disposition__name__iexact="available",
            asset_types__in=asset.asset_types.all())
        serializer = self.serializer_class(procedures.distinct(), many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get',],
        serializer_class=AssetSerializer,
    )
    def stressors(self, request, pk=None):
        """
        Returns all assets that can perform procedures in the "Stressors" group
        """
        self.context={'request':request}
        assets = Asset.objects.filter(asset_types__proceduredefinition__group__name__iexact='stressors')
        serializer = self.serializer_class(assets.distinct(), many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['get',],
        serializer_class=AssetSerializer,
    )
    def units(self, request, pk=None):
        """
        Returns all of the units currently under stress in/on this asset
        """
        self.context={'request':request}
        # asset = Asset.objects.get(id=pk)
        # disposition = Disposition.objects.get(name__iexact="in progress")
        units = Unit.objects.filter(
            procedureresult__disposition__name__iexact="in progress",
            procedureresult__stepresult__measurementresult__asset__id=pk,
        ).distinct()
        if not units:
            return Response ({})
        master_data_frame = pd.DataFrame(list(units.values(
            'serial_number',
            'location__name',
            'fixture_location__name',
            'procedureresult__test_sequence_definition__name',
            # 'procedure_definition__name',
            'workorder__project__number',
            'workorder__name',
            'workorder__project__customer__name',
            'procedureresult__name',
            'procedureresult__start_datetime',
            'procedureresult__procedure_definition__aggregate_duration',
            # 'allow_skip',
            )))
        full=[]
        filled = master_data_frame.fillna('foo') # this needs removal
        filled['procedureresult__procedure_definition__aggregate_duration'] = pd.to_timedelta(filled.procedureresult__procedure_definition__aggregate_duration, unit='m')
        filled['eta_datetime'] = filled['procedureresult__start_datetime'] + filled['procedureresult__procedure_definition__aggregate_duration']

        filled.columns = [
            'serial_number',
            'location',
            'fixture_location',
            'test_sequence',
            'project_number',
            'work_order',
            'customer',
            'execution_group_name',
            'start_datetime',
            'procedure_duration',
            'eta_datetime',
            ]
        # grouped = master_data_frame.groupby('serial_number')
        # for name, group in grouped:
        #     full[name]=group.to_dict(orient='records')
        full = filled.to_dict(orient='records')
        return Response(full)
