import json

from django.utils import timezone
from django.db import IntegrityError, transaction
from django.contrib.auth.models import User

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_tracking.mixins import LoggingMixin
from rest_framework import status
from rest_framework.status import (HTTP_400_BAD_REQUEST)

from lsdb.models import AvailableDefect
from lsdb.models import AzureFile
from lsdb.models import MeasurementResult
from lsdb.models import DispositionCode
from lsdb.models import Disposition
from lsdb.models import Asset

from lsdb.utils.Limits import within_limits
from lsdb.serializers import MeasurementResultSerializer
from lsdb.serializers import AzureFileSerializer
from lsdb.serializers import DispositionCodeListSerializer
from lsdb.permissions import ConfiguredPermission

class MeasurementResultViewSet(LoggingMixin, viewsets.ModelViewSet):
    """
    API endpoint that allows MeasurementResult to be viewed or edited.
    """
    logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
    queryset = MeasurementResult.objects.all()
    serializer_class = MeasurementResultSerializer
    permission_classes = [ConfiguredPermission]

    @action(detail=False, methods=['get',],
        serializer_class=DispositionCodeListSerializer,
    )
    def dispositions(self, request, pk=None):
        self.context={'request':request}
        serializer = DispositionCodeListSerializer(DispositionCode.objects.get(
            name='measurement_results'),
            many=False,
            context={'request': request})
        return Response(serializer.data)

    # @action(detail=True, methods=['get','post'],
    #     serializer_class=AzureFileSerializer,
    # )
    # def attach(self, request, pk=None):
    #     self.context={'request':request}
    #     queryset = MeasurementResult.objects.get(id=pk)
    #     if request.method == 'POST':
    #         serializer = AzureFileSerializer(data=request.data,context={'request': request})
    #         if serializer.is_valid():
    #             attachment = serializer.save()
    #             queryset.result_files.add(attachment)
    #             queryset.save()
    #         # create a new attachment attached to this crate
    #     if request.method == 'GET':
    #         serializer = MeasurementResultSerializer(queryset, many=False, context=self.context)
    #     return Response(serializer.data)

    @transaction.atomic
    @action(detail=True, methods=['get','post'],
        serializer_class=MeasurementResultSerializer,
    )
    def link_files(self, request, pk=None):
        """
        This action will link an existing AzureFile to this measurement_result.
        POST: {"id":1} to link azurfefile id=1 to this measurement_result
        """
        self.context={'request':request}
        queryset = MeasurementResult.objects.get(id=pk)
        if request.method == 'POST':
            params = request.data
            file_id = params.get('id')
            if file_id:
                attachment = AzureFile.objects.get(id=int(file_id))
                queryset.result_files.add(attachment)
                queryset.save()
        serializer = MeasurementResultSerializer(queryset, many=False, context=self.context)
        return Response(serializer.data)

    @transaction.atomic
    @action(detail=True, methods=['get','post'],
        serializer_class=MeasurementResultSerializer,
    )
    def submit(self, request, pk=None):
        """
        This action accepts a minimum amount of data in order to POST results to a Measurement Result
        POST:
        {
            "location": null,
            "software_revision": "0.0",
            "disposition": <-- ID
            "result_double": null,
            "result_datetime": null,
            "result_string": null,
            "result_boolean": null,
            "reviewed_by_user": <-- username
            "review_datetime": null,
            "notes": null,
            "tag": null,
            "station": 0,
            "start_datetime": null,
            "duration": null,
            "asset": <-- ID
            "do_not_include": false,
            "requires_review": true,
            "order": 3,
            "report_order": 3,
        }
        We can also do history here:
        POST:
        {
            "historic":true,
            "user":user URL of the selected user
            "datetime": datetime of the historic measurement # Deprecated, use "start_datetime"
            "location": null,
            "software_revision": "0.0",
            "disposition": <-- ID
            "result_double": null,
            "result_datetime": null,
            "result_string": null,
            "result_boolean": null,
            "reviewed_by_user": NOT REQUIRED FOR HISTORIC
            "review_datetime": NOT REQUIRED FOR HISTORIC
            "notes": null,
            "tag": null,
            "station": 0,
            "start_datetime": null,
            "duration": null,
            "asset": <-- ID
            "do_not_include": false,
            "requires_review": true,
            "order": 3,
            "report_order": 3,
        }
        """
        self.context={'request':request}
        result = MeasurementResult.objects.get(id=pk)
        if request.method == 'POST':
            params = request.data
            # TODO: Solve the "requires_review" logic for setting the disposition.
            # Lookups and translations:
            if params.get('disposition'):
                result.disposition = Disposition.objects.get(id=params.get('disposition'))
            if params.get('asset'):
                result.asset = Asset.objects.get(id=params.get('asset'))
            if params.get('result_defect') and (type(params.get('result_defect'))== int ):
                result.result_defect = AvailableDefect.objects.get(id=params.get('result_defect'))
            if params.get('reviewed_by_user'):
                result.reviewed_by_user = User.objects.get(username=params.get('reviewed_by_user'))
            # Special cases for hsitoric. KLUGE
            if params.get('historic'):
                # overrides for current user to be reviewer:
                result.reviewed_by_user = request.user
                result.review_datetime = timezone.now().isoformat()
                if params.get('user'):
                    user = params.get('user')
                    if type(user) == int:
                        result.user = User.objects.get(id=user)
                    else:
                        result.user = user
                else:
                    return Response({'error': 'user required for historic entry'},
                                status=status.HTTP_400_BAD_REQUEST)
                if params.get('start_datetime'):
                    result.start_datetime = params.get('start_datetime')
                else:
                    return Response({'error': 'start_datetime required for historic entry'},
                                status=status.HTTP_400_BAD_REQUEST)
                if params.get('disposition'):
                     pass
                else:
                    return Response({'error': 'disposition required for historic entry'},
                                status=status.HTTP_400_BAD_REQUEST)
            else:
                # NOT a historic POST:
                result.user = request.user
            # Everything else
            result.date_time = timezone.now().isoformat()
            result.software_revision = params.get('software_revision', result.software_revision)
            result.result_double = params.get('result_double', result.result_double)
            result.result_datetime = params.get('result_datetime', result.result_datetime)
            result.result_string = params.get('result_string', result.result_string)
            result.result_boolean = params.get('result_boolean', result.result_boolean)
            result.review_datetime = params.get('review_datetime', result.review_datetime)
            result.notes = params.get('notes', result.notes)
            result.tag = params.get('tag', result.tag)
            result.station = params.get('station', result.station)
            result.start_datetime = params.get('start_datetime', result.start_datetime)
            result.duration = params.get('duration', result.duration)
            result.do_not_include = params.get('do_not_include', result.do_not_include)
            result.requires_review = params.get('requires_review', result.requires_review)
            result.order = params.get('order', result.order)
            result.report_order = params.get('report_order', result.report_order)
            result.save()

        serializer = MeasurementResultSerializer(result, many=False, context=self.context)
        return Response(serializer.data)
