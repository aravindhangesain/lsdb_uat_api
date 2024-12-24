# import json
from django.contrib.auth.models import User
from django.db import IntegrityError, transaction
from django.db.models import Q
from django.utils import timezone

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework_tracking.mixins import LoggingMixin
from rest_framework.status import (HTTP_400_BAD_REQUEST)

from lsdb.models import Asset, AvailableDefect
from lsdb.models import Location
from lsdb.models import StepResult
from lsdb.models import Disposition
from lsdb.models import DispositionCode
from lsdb.models import MeasurementResult
from lsdb.models import MeasurementDefinition

from lsdb.serializers import StepResultSerializer
from lsdb.serializers import DispositionCodeListSerializer
from lsdb.serializers import MeasurementResultSerializer
from lsdb.permissions import ConfiguredPermission


class StepResultViewSet(LoggingMixin, viewsets.ModelViewSet):
    """
    API endpoint that allows StepResult to be viewed or edited.
    """
    logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
    queryset = StepResult.objects.all()
    serializer_class = StepResultSerializer
    permission_classes = [ConfiguredPermission]

    @action(detail=False, methods=['get',],
        serializer_class=DispositionCodeListSerializer,
    )
    def dispositions(self, request, pk=None):
        self.context={'request':request}
        serializer = DispositionCodeListSerializer(DispositionCode.objects.get(
            name='step_results'),
            many=False,
            context={'request': request})
        return Response(serializer.data)

    @transaction.atomic
    @action(detail=True, methods=['get','post'],
        serializer_class=MeasurementResultSerializer,
    )
    def add_measurement(self, request, pk=None):
        """
        This action accepts a minimum amount of data in order to POST results to a NEW Measurement Result attached to this step.
        POST:
        {
            "user": ID
            "measurement_definition": ID
            "disposition": ID
            "asset": ID
            "date_time": YYYY-MM-DD HH:MM[:ss[.uuuuuu]][TZ] format,
            "location": ID,
            "software_revision": String,
            "result_defect": ID,
            "result_double": FloatField,
            "result_datetime": YYYY-MM-DD HH:MM[:ss[.uuuuuu]][TZ] format,
            "result_string": String,
            "result_boolean": Boolean,
            "reviewed_by_user": username,
            "review_datetime": YYYY-MM-DD HH:MM[:ss[.uuuuuu]][TZ] format,
            "notes": String,
            "tag": String,
            "station": Integer,
            "start_datetime": YYYY-MM-DD HH:MM[:ss[.uuuuuu]][TZ] format,
            "duration": Integer,
            "do_not_include": Boolean,
            "order": Integer,
            "report_order": Integer,
        }
        """
        self.context={'request':request}
        step_result = StepResult.objects.get(id=pk)
        if request.method == 'POST':
            params = request.data

            disposition = params.get('disposition')
            reviewed_by_user = params.get('reviewed_by_user')
            asset = params.get('asset')
            user = params.get('user')
            location = params.get('location')
            result_defect = params.get('result_defect')

            if disposition and (type(disposition) == int):
                disposition = Disposition.objects.get(id=disposition)
            if reviewed_by_user:
                reviewed_by_user = User.objects.get(username=reviewed_by_user)
            if asset and (type(asset) == int ):
                asset = Asset.objects.get(id=asset)
            if user and (type(user) == int ):
                user = User.objects.get(id=user)
            if location and (type(location) == int ):
                location = Location.objects.get(id=location)
            if result_defect and (type(result_defect) == int ):
                result_defect = AvailableDefect.objects.get(id=result_defect)

            # This is the only strictly required param from the POST:
            measurement_definition = params.get('measurement_definition')
            if type(measurement_definition) == int:
                measurement_definition = MeasurementDefinition.objects.get(id=measurement_definition)
            # else:
            #    check the object if it's not valid throw a 400

            measurement_result = MeasurementResult.objects.create(
                date_time =  timezone.now().isoformat(),
                step_result = step_result,
                measurement_definition = measurement_definition,
                user = user,
                location = location,
                software_revision = params.get('software_revision',0.0),
                disposition = disposition,
                result_defect = params.get('result_defect'),
                result_double = params.get('result_double'),
                result_datetime = params.get('result_datetime'),
                result_string = params.get('result_string'),
                result_boolean = params.get('result_boolean'),
                limit = measurement_definition.limit,
                reviewed_by_user = reviewed_by_user,
                review_datetime = params.get('review_datetime'),
                notes = params.get('notes'),
                tag = params.get('tag'),
                station = params.get('station',0),
                start_datetime = params.get('start_datetime'),
                duration = params.get('duration'),
                asset = asset,
                do_not_include = params.get('do_not_include',False),
                name = measurement_definition.name,
                record_only = measurement_definition.record_only,
                allow_skip = measurement_definition.allow_skip,
                requires_review = measurement_definition.requires_review,
                measurement_type = measurement_definition.measurement_type,
                order = measurement_definition.order,
                report_order = measurement_definition.report_order,
                measurement_result_type = measurement_definition.measurement_result_type,
            )
            serializer = MeasurementResultSerializer(measurement_result, many=False, context=self.context)
        else:
            serializer = StepResultSerializer(step_result, many=False, context=self.context)
        return Response(serializer.data)

    @transaction.atomic
    @action(detail=True, methods=['get','post'],
        serializer_class=StepResultSerializer,
    )
    def submit(self, request, pk=None):
        """
        Accepts a sparse POST of:
        {
        "disposition": ID,
        "start_datetime": YYYY-MM-DD HH:MM[:ss[.uuuuuu]][TZ] format,
        "notes": String,
        "duration": Integer,
        "execution_number": Integer,
        "archived": Boolean,
        "test_step_result": ID,
        }
        """
        self.context={'request':request}
        result = StepResult.objects.get(id=pk)
        if request.method == 'POST':
            params = request.data
            if params.get('disposition'):
                disposition = Disposition.objects.get(id=params.get('disposition'))
                if disposition.complete:
                    # check all of your measurementresults
                    if (result.measurementresult_set.all().count()) and ( # there are result children
                        result.measurementresult_set.all().count() != result.measurementresult_set.filter(Q(disposition__complete=True)|Q(allow_skip=True)).count()):
                        # error case:
                        return Response({'message':'One or more measurements attached to this step are not complete and cannot be skipped'}, status = HTTP_400_BAD_REQUEST)
                # all good, set the disposition to the incoming one:
                result.disposition = disposition
            if params.get('test_step_result'):
                result.test_step_result = StepResult.objects.get(id=params.get('test_step_result'))
            result.start_datetime = params.get('start_datetime', result.start_datetime)
            result.notes = params.get('notes', result.notes)
            result.execution_number = params.get('execution_number', result.execution_number)
            result.archived = params.get('archived', result.archived)
            result.save()

        serializer = StepResultSerializer(result, many=False, context=self.context)
        return Response(serializer.data)

    @transaction.atomic
    @action(detail=True, methods=['get','post'],
        serializer_class=StepResultSerializer,
    )
    def retest(self, request, pk=None):
        """
        Accepts a sparse POST of:
        {
        stubbed
        }
        This action needs to mark the current step result archived=true
        """
        self.context={'request':request}
        result = StepResult.objects.get(id=pk)
        #result.archived = True
        #rebuild me
        serializer = StepResultSerializer(result, many=False, context=self.context)
        return Response(serializer.data)
