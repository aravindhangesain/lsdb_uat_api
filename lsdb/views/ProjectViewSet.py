import datetime
import json
import zipfile
from io import BytesIO

import numpy as np
from PIL import Image, ImageOps
from django.db import IntegrityError, transaction
from django.db.models import Q, Sum, Max, Min, F
from django.http import HttpResponse
from django.utils import timezone
from django_filters import rest_framework as filters
import requests
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.status import (HTTP_400_BAD_REQUEST)
from rest_framework_extensions.mixins import DetailSerializerMixin
from rest_framework_tracking.mixins import LoggingMixin

from lsdb.models import ActionDefinition
from lsdb.models import AzureFile
from lsdb.models import Disposition
from lsdb.models import MeasurementResult
from lsdb.models import PlexusImport
from lsdb.models import ProcedureResult
from lsdb.models import Project
from lsdb.models import TestSequenceDefinition
from lsdb.models import Unit
from lsdb.models import WorkOrder,LocationLog
from lsdb.models import Customer
from lsdb.permissions import ConfiguredPermission, IsAdminOrSelf
from lsdb.serializers.GetActiveProjectsDataGridSerializer import GetActiveProjectsDataGridSerializer
from lsdb.serializers.ActionResultSerializer import ActionResultSerializer
from lsdb.serializers.NoteSerializer import NoteSerializer
from lsdb.serializers.ProjectDetailSerializer import ProjectDetailSerializer
from lsdb.serializers.ProjectSerializer import ProjectSerializer
from lsdb.serializers.UnitListSerializer import UnitListSerializer
from lsdb.serializers.WorkOrderDataSerializer import WorkOrderDataListSerializer
from lsdb.serializers.WorkOrderSerializer import WorkOrderProjectSerializer
from lsdb.serializers.WorkOrderSerializer import WorkOrderSerializer
from lsdb.utils import ExcelFile
# from lsdb.utils.NoteUtils import create_note
from lsdb.utils.ActionUtils import create_action
from lsdb.utils.HasHistory import unit_minutes
from lsdb.utils.ObjFromUrl import obj_from_url
# from datetime import strftime
from lsdb.utils.ZipFileUtils import create_download_file
from datetime import date


class ProjectFilter(filters.FilterSet):
    class Meta:
        model = Project
        fields = [
            'number',
            'customer',
        ]


class ProjectViewSet(DetailSerializerMixin, LoggingMixin, viewsets.ModelViewSet):
    """
    API endpoint that allows Project to be viewed or edited.
    """
    logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
    queryset = Project.objects.all().prefetch_related('units')
    # ProcedureResult.objects.filter(work_order=work_order).order_by(
    #     'linear_execution_group').select_related('unit').prefetch_related('stepresult_set__measurementresult_set')
    serializer_class = ProjectSerializer
    serializer_detail_class = ProjectDetailSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = ProjectFilter
    permission_classes = [ConfiguredPermission]


    @action(detail=False, methods=['get'],
            permission_classes=(ConfiguredPermission,),
            serializer_class=WorkOrderDataListSerializer)
    def download(self, request):
        """
        This is the place where we can see the list of projects and be able to GET
        data to be downloaded. WorkOrder IDs must be included on the query parameters
        as a comma separated list:
        `/api/1.0/projects/download/?ids=84,85`

        Process of Downloading:
        1. Get workorders from parameters and create a queryset of them.
        2. Iterate over each workorder and get all Units related to the workorder. Open excel files for vi, wl, dt, color, el.
        3. Iterate over each Unit and get all procedure results related to the unit.
        4. Iterate over result, and write the data to the correct locations.
        """
        self.context = {'request': request}
        params = {}
        workorder_ids = request.query_params.get('workorder_ids')
        unit_ids = request.query_params.get('unit_ids')
        procedure_ids = request.query_params.get('procedure_ids')
        TSD_ids = request.query_params.get('test_sequence_definition_ids')
        adjust_images = request.query_params.get('adjust_images')

        # This will convert anything not 'true' to False
        str2bool = lambda string: string is not None and string.upper() == 'TRUE'

        if workorder_ids:
            # print('There are work order ids')
            params["workorder_ids"] = workorder_ids.split(',')

            if unit_ids:
                params["unit_ids"] = unit_ids.split(',')
            else:
                params["unit_ids"] = None

            if procedure_ids:
                params["procedure_ids"] = procedure_ids.split(',')
            else:
                params["procedure_ids"] = None

            if TSD_ids:
                params["test_sequence_definition_ids"] = TSD_ids.split(',')
            else:
                params["test_sequence_definition_ids"] = None

            queryset = WorkOrder.objects.filter(id__in=params["workorder_ids"])

            return create_download_file(work_orders=queryset, tsd_ids=params['test_sequence_definition_ids'],
                                        unit_ids=params['unit_ids'], procedure_ids=params['procedure_ids'],
                                        adjust_images=str2bool(adjust_images))
        else:
            # print('There are no work order ids')
            queryset = WorkOrder.objects.all()
        serializer = WorkOrderDataListSerializer(queryset, many=True, context=self.context)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], permission_classes=(ConfiguredPermission,),
            serializer_class=WorkOrderDataListSerializer)
    def download_project(self, request, pk=None):
        self.context = {'request': request}
        project = Project.objects.get(pk=pk)
        work_orders = project.workorder_set.all()

        response = create_download_file(work_orders=work_orders, tsd_ids=[], unit_ids=[], procedure_ids=[])

        print(response.headers)

        return response

    @action(detail=False, methods=['get'],
            permission_classes=(ConfiguredPermission,),
            serializer_class=WorkOrderDataListSerializer)
    def download_deprecated(self, request, pk=None):
        """
        This is the place where we can see the list of projects and be able to GET
        data to be downloaded. WorkOrder IDs must be included on the query parameters
        as a comma separated list:
        `/api/1.0/projects/download/?ids=84,85`
        """
        self.context = {'request': request}
        ids = request.query_params.get('ids')
        if ids:
            params = ids.split(',')
            # params = json.loads(request.body)
            # procedure_results = ProcedureResult.objects.filter(work_order__in=params)
            queryset = WorkOrder.objects.filter(id__in=params)
            mem_zip = BytesIO()
            with zipfile.ZipFile(mem_zip, mode='w', compression=zipfile.ZIP_DEFLATED) as zf:
                for work_order in queryset:
                    # zf.debug = 3
                    serializer = WorkOrderSerializer(work_order, many=False, context=self.context)
                    results = ProcedureResult.objects.filter(work_order=work_order).order_by(
                        'test_sequence_definition', 'linear_execution_group').select_related('unit').prefetch_related(
                        'stepresult_set__measurementresult_set')
                    # module = Workbook()
                    # module_sheet = module.active
                    module = '"Manufacturer","Technology","Model","Serial Number","Calibration Device Used","Maximum Voltage[V]","Width [mm]","Height [mm]","Pmax [W]","VOC [V]","VMP[V]","ISC [A]","IMP [A]"\n'
                    units = Unit.objects.filter(procedureresult__work_order=work_order).distinct()
                    for unit in units:
                        module += '"{}","{}","{}","=""{}""","{}",{},{},{},{},{},{},{},{}\n'.format(
                            unit.unit_type.manufacturer.name,
                            unit.unit_type.module_property.module_technology,
                            unit.unit_type.model,
                            unit.serial_number,
                            None,
                            unit.unit_type.module_property.system_voltage,
                            unit.unit_type.module_property.module_width,
                            unit.unit_type.module_property.module_height,
                            unit.unit_type.module_property.nameplate_pmax,
                            unit.unit_type.module_property.voc,
                            unit.unit_type.module_property.vmp,
                            unit.unit_type.module_property.isc,
                            unit.unit_type.module_property.imp
                        )
                    zf.writestr('{}/{}_modules.csv'.format(
                        work_order.project.number,
                        work_order.name,
                    ), module)

                    tests = TestSequenceDefinition.objects.filter(procedureresult__work_order=work_order).distinct()
                    for test in tests:
                        results = ProcedureResult.objects.filter(work_order=work_order,
                                                                 test_sequence_definition=test).order_by(
                            'linear_execution_group').select_related('unit').prefetch_related(
                            'stepresult_set__measurementresult_set')
                        csv = {}
                        for result in results:
                            print(result, result.name)
                            if not csv.get(result.name):
                                csv[result.name] = {}
                            if not csv.get(result.name).get(result.procedure_definition.name):
                                rowcount = 0
                                csv[result.name][result.procedure_definition.name] = {
                                    'header': ['Measurement', 'Serial Number'], 'body': []}
                            # csv +='"{}","{}","{}","{}"'.format(
                            #     result.procedure_definition.name,
                            #     result.name,
                            #     result.unit.unit_type.model,
                            #     result.unit.serial_number,
                            # )
                            for step_result in result.stepresult_set.all().exclude(archived=True):
                                # These should be ordered by report_order
                                # Skip any measurement with a report order=0
                                csv[result.name][result.procedure_definition.name]['body'].append(step_result.name)
                                csv[result.name][result.procedure_definition.name]['body'].append(
                                    '=""{}""'.format(result.unit.serial_number))

                                for measurement in step_result.measurementresult_set.all().order_by('report_order'):
                                    # Kluge: use the defintion report order
                                    if measurement.measurement_definition.report_order == 0:
                                        # TODO: Nuke the step if it exists, no more empty files
                                        continue
                                    if rowcount == 0:
                                        # print('head',result.name,measurement.name,measurement.measurement_type.name)
                                        csv[result.name][result.procedure_definition.name]['header'].append(
                                            measurement.measurement_type.name)
                                    if measurement.measurement_result_type.name == 'result_files':
                                        if measurement.result_files.all().count():
                                            for azurefile in measurement.result_files.all():
                                                filetype = ''
                                                # KLUGE: This should be detecting the Azurefile type with magic here:
                                                if azurefile.file.name.lower().endswith(('xls', 'xlsx', 'txt', 'csv')):
                                                    filetype = 'DataFiles'
                                                else:
                                                    filetype = 'ImageFiles'

                                                bytes = azurefile.file.file.read()

                                                csv[result.name][result.procedure_definition.name]['body'].append(
                                                    azurefile.file.name)
                                                zf.writestr('{}/{}/{}/{}/{}/{}'.format(
                                                    work_order.project.number,
                                                    work_order.name,
                                                    test.name,
                                                    filetype,
                                                    result.name,
                                                    azurefile.file.name,
                                                ),
                                                    bytes)
                                        else:
                                            csv[result.name][result.procedure_definition.name]['body'].append('N/A')
                                    elif step_result.name == "Measure Color" and measurement.measurement_result_type.name == "result_string":
                                        if measurement.result_string == None:
                                            csv[result.name][result.procedure_definition.name]['body'].append('N/A')
                                        else:
                                            # Convert meassurement string to data values
                                            data = json.loads(measurement.result_string)
                                            data = data["values"]

                                            excel_file = ExcelFile()
                                            sheet = excel_file.workbook.active
                                            # Header Rows
                                            sheet.append([
                                                "Position",
                                                "L*",
                                                "A*",
                                                "B*"
                                            ])

                                            # Append values to sheet, create columns as we go
                                            l_val, a_val, b_val = [], [], []

                                            for value in data:
                                                row = [value["position"], value["l_value"], value["a_value"],
                                                       value["b_value"]]
                                                l_val.append(value["l_value"])
                                                a_val.append(value["a_value"])
                                                b_val.append(value["b_value"])
                                                sheet.append(row)

                                            sheet.append(
                                                ["Average", np.average(l_val), np.average(a_val), np.average(b_val)])

                                            sheet.append(["STD", np.std(l_val), np.std(a_val), np.std(b_val)])

                                            filename = 'ColorimeterReport-{}.xlsx'.format(
                                                timezone.now().strftime('%b-%d-%Y-%H%M%S'))
                                            csv[result.name][result.procedure_definition.name]['body'].append(filename)
                                            zf.writestr('{}/{}/{}/{}/{}'.format(
                                                work_order.project.number,
                                                work_order.name,
                                                test.name,
                                                result.name,
                                                filename,
                                            ),
                                                excel_file.get_memory_file().read())
                                    else:
                                        # These also should be in report order
                                        # Skip any measurement with a report order=0
                                        # https://superuser.com/questions/568429/excel-csv-import-treating-quoted-strings-of-numbers-as-numeric-values-not-strin
                                        csv[result.name][result.procedure_definition.name]['body'].append(
                                            getattr(measurement, measurement.measurement_result_type.name))
                                csv[result.name][result.procedure_definition.name]['body'].append('\n')
                                rowcount += 1
                        # this is too deep
                        for report in csv.keys():
                            for procedure in csv[report].keys():
                                report_string = ''
                                for hval in csv[report][procedure]['header']:
                                    report_string += '"{}",'.format(hval)
                                report_string += '\n'
                                # print('BVAL',len(csv[report][procedure]['body']))
                                for bval in csv[report][procedure]['body']:
                                    if bval == '\n':
                                        report_string += '\n'
                                    else:
                                        report_string += '"{}",'.format(bval)
                                # report_string = print(csv[report]['header'])
                                if len(csv[report][procedure]['header']):  # prevent writing empty files
                                    zf.writestr('{}/{}/{}/{}/{}_data.csv'.format(
                                        work_order.project.number,
                                        work_order.name,
                                        test.name,
                                        report,
                                        procedure
                                    ), report_string)

            filename = timezone.now().strftime('%b-%d-%Y-%H%M%S')
            response = HttpResponse(mem_zip.getvalue(), content_type='application/x-zip-compressed')
            response['Content-Disposition'] = 'attachment; filename={}.zip'.format(filename)
            return response
        else:
            queryset = WorkOrder.objects.all()
        serializer = WorkOrderDataListSerializer(queryset, many=True, context=self.context)
        return Response(serializer.data)

    @action(detail=True, methods=['get', ]
            )
    def actions(self, request, pk=None):
        """
        a GET on this action will return all of the actions on the current project
        and all of the child work orders:
        {
            "actions":[
                {
                    "name":"",
                    "description":"",
                    ...
                },
                {}
            ],
            "total_actions":#,
            "completed_actions":#,
            "work_orders":[
                {
                    "id":1,
                    "name":"BOM1"
                    "actions":[
                        {},
                        {}
                    ],
                    "total_actions":#,
                    "completed_actions":#
                }
            ]
        }
        """
        action_values = ['id', 'name', 'description', 'disposition__name', 'execution_group',
                         'completion_criteria',
                         'done_datetime', 'start_datetime', 'promise_datetime', "eta_datetime"]
        self.context = {'request': request}
        project = Project.objects.prefetch_related('actions', 'workorder_set').get(id=pk)
        response_dict = {'work_orders': []}
        actions = project.actions.prefetch_related('completion_criteria', 'actioncompletionresult_set').all().order_by(
            'execution_group').select_related('disposition')
        actions_dict = actions.values(*action_values)

        response_dict['actions'], response_dict['total_actions'], response_dict[
            'completed_actions'] = self._actions_obj(actions, actions_dict)

        work_orders = project.workorder_set.all()
        for work_order in work_orders:
            wo_dict = {
                'id': work_order.id,
                'name': work_order.name
            }
            wo_dict['actions'] = []

            actions = work_order.actions.prefetch_related('completion_criteria',
                                                          'actioncompletionresult_set').all().order_by(
                'execution_group').select_related('disposition')
            actions_dict = actions.values(*action_values)
            wo_dict['actions'], wo_dict['total_actions'], response_dict['completed_actions'] = self._actions_obj(
                actions, actions_dict)
            # wo_dict['total_actions'] = work_order.actions.all().count()
            if work_order.actions.all().count():
                wo_dict['completed_actions'] = work_order.actions.filter(disposition__complete=True).count()
            else:
                wo_dict['completed_actions'] = 0
            response_dict['work_orders'].append(wo_dict)
        # response_dict['work_orders'] = project.workorder_set.all().values('id','name')
        return Response(response_dict)

    def _actions_obj(self, actions, actions_dict):
        """
        Internal method to return a list of serialized action objects
        """
        actions_list = []
        for action_result in actions_dict:
            actions_obj = actions.get(id=action_result['id'])
            result_dict = action_result
            result_dict['completion_criteria'] = []
            for criterion in actions_obj.actioncompletionresult_set.select_related(
                    'action_completion_definition').all():
                result_dict['completion_criteria'].append({
                    'criteria_id': criterion.id,
                    "action_completion_definition": criterion.action_completion_definition.name,
                    "criteria_completed": criterion.criteria_completed,
                    "completed_datetime": criterion.completed_datetime,
                })
            actions_list.append(result_dict)
        if actions.count() > 0:
            completed_actions = actions.filter(disposition__complete=True).count()
        else:
            completed_actions = 0

        return actions_list, actions.count(), completed_actions

    @transaction.atomic
    @action(detail=True, methods=['get', 'post'],
            serializer_class=ActionResultSerializer,
            )
    def new_action(self, request, pk=None):
        """
        This endpoint can be used to create a new ActionResult bucket that is not specifically tied
        to a ActionPlanDefinition, but is tied to this project.
        POST:
        {
                "name":"", Required
                "description":"",
                "disposition":$ID,Required
                "action_definition":$ID,Required
                "execution_group":"", optional
                "done_datetime":"YYYY-MM-DD HH:MM[:ss[.uuuuuu]][TZ] format",
                "start_datetime":"YYYY-MM-DD HH:MM[:ss[.uuuuuu]][TZ] format",
                "promise_datetime":"YYYY-MM-DD HH:MM[:ss[.uuuuuu]][TZ] format",
                "eta_datetime":"YYYY-MM-DD HH:MM[:ss[.uuuuuu]][TZ] format",
                "groups":[
                    ID(s)
                ]
       }
        """
        self.context = {'request': request}
        if request.method == 'POST':
            params = request.data
            disposition = params.get('disposition')
            if disposition and (type(disposition) == int):
                disposition = Disposition.objects.get(id=disposition)
            groups = params.get('groups')
            parent_object = Project.objects.get(pk=pk)
            action_definition = ActionDefinition.objects.get(id=params.get('action_definition'))

            action, status = create_action(
                action_definition=action_definition,
                disposition=disposition,
                groups=groups,
                parent_object=parent_object,
                request_params=params,
            )
            if status:  # Action was created
                serializer = ActionResultSerializer(action, many=False, context=self.context)
            else:  # action contains an error from IntegrityError
                return Response({"error": action.__str__()}, status=HTTP_400_BAD_REQUEST)
        else:  # GET
            serializer = ActionResultSerializer([], many=True, context=self.context)
        return Response(serializer.data)

    @action(detail=True, methods=['get', ],
            serializer_class=NoteSerializer,
            )
    def notes(self, request, pk=None):
        self.context = {'request': request}
        project = Project.objects.get(id=pk)
        note_type = request.query_params.get('type')
        if note_type:
            queryset = project.notes.filter(note_type__id=note_type)
        else:
            queryset = project.notes.all()
        serializer = NoteSerializer(queryset, many=True, context=self.context)
        return Response(serializer.data)

    @action(detail=True, methods=['get'],
            permission_classes=(ConfiguredPermission,),
            serializer_class=ProjectSerializer)
    def available_units(self, request, pk=None):
        """
        This action returns all of the project units that are available for assignment to a work order
        by eliminating any of them that are already attached to work orders (history not withstanding)
        """
        self.context = {'request': request}
        project = Project.objects.get(id=pk)
        units = project.units.filter(workorder__isnull=True)

        serializer = UnitListSerializer(units, many=True, context=self.context)
        return Response(serializer.data)

    @action(detail=True, methods=['get', 'put', 'patch'],
            permission_classes=(ConfiguredPermission,),
            serializer_class=ProjectSerializer)
    def edit(self, request, pk=None):
        """
        This action allows the non-unit fields of a Project to be edited. PUT and PATCH are treated the same.
        DOES NOT UPDATE CUSTOMER
        """
        self.context = {'request': request}
        project = Project.objects.get(id=pk)
        if request.method in ['PUT', 'PATCH']:
            # print(request.data)
            project.notes = request.data.get('notes', project.notes)
            project.number = request.data.get('number', project.number)
            project.sfdc_number = request.data.get('sfdc_number', project.sfdc_number)
            if request.data.get('project_manager'):
                project.project_manager = obj_from_url(request.data.get('project_manager'))
            # if request.data.get('customer'):
            #     project.customer = obj_from_url(request.data.get('customer'))
            if request.data.get('group'):
                project.group = obj_from_url(request.data.get('group'))
            if request.data.get('disposition'):
                project.disposition = obj_from_url(request.data.get('disposition'))
            if request.data.get('proposal_price'):
                project.proposal_price = obj_from_url(request.data.get('proposal_price'))
            project.save()
        serializer = ProjectSerializer(project, many=False, context=self.context)
        return Response(serializer.data)

    @action(detail=True, methods=['get', 'post'],
            permission_classes=(ConfiguredPermission,),
            serializer_class=ProjectSerializer,
            )
    def link_units(self, request, pk=None):
        """
        This action endpoint is used to link units to the Project.
        to add uints to a project, POST the following:
        [
        "1","2"
        ]
        The keys represent the units to attach. There is not a history event, so a simple list of IDs id the right interface.
        """
        self.context = {'request': request}
        project = Project.objects.get(id=pk)
        if request.method == "POST":
            # do the needful
            params = json.loads(request.body)
            for key in params:
                # TODO: Wrap this with exception handler
                unit = Unit.objects.get(id=key)
                project.units.add(unit)
                project.save()
        serializer = ProjectSerializer(project, many=False, context=self.context)
        return Response(serializer.data)

    @action(detail=True, methods=['get', 'post'],
            permission_classes=(ConfiguredPermission,),
            serializer_class=ProjectSerializer,
            )
    def unlink_units(self, request, pk=None):
        """
        This action endpoint is used to unlink units from the work order
        [
        "1","2"
        ]
        """
        self.context = {'request': request}
        project = Project.objects.get(id=pk)
        if request.method == "POST":
            params = json.loads(request.body)
            for key in params:
                unit = Unit.objects.get(id=key)
                project.units.remove(unit)
                project.save()

        serializer = ProjectSerializer(project, many=False, context=self.context)
        return Response(serializer.data)

    @transaction.atomic
    @action(detail=True, methods=['get', 'post'],
            serializer_class=ProjectSerializer,
            permission_classes=[IsAdminOrSelf, ConfiguredPermission, ]
            )
    def merge(self, request, pk=None):
        """
        This action is used to add another project object's data to this one .
        POST:
        {
            "id": ID
        }
        DANGER DANGER DANGER DELETES OBJECTS
        preseves old data if it exists for:
        sfdc_number
        customer
        group
        start_date
        invoice_date
        proposal_price
        {"id":407}
        """
        # this actually could be a general collapse, but not for 1.0
        # TODO: Make this process more general and more bullet proof
        self.context = {'request': request}
        project = Project.objects.get(id=pk)
        if request.method == "POST":
            params = json.loads(request.body)
            obsolete = Project.objects.get(id=params.get('id'))
            work_orders = project.workorder_set.all()
            for note in obsolete.notes.all():
                project.notes.add(note)
                obsolete.notes.remove(note)
            for sri_note in obsolete.sri_notes.all():
                project.sri_notes.add(sri_note)
                obsolete.sri_notes.remove(sri_note)
            for unit in obsolete.units.all():
                project.units.add(unit)
                obsolete.units.remove(unit)
            for expected_unit in obsolete.expectedunittype_set.all():
                expected_unit.project = project
                expected_unit.save()
            for work_order in obsolete.workorder_set.all():
                try:
                    work_order.project = project
                    work_order.save()
                except IntegrityError:
                    # if there is a work_order with the same name here...
                    work_order.name = 'imported_{}'.format(work_order.name)
                    # Looks like I thought about conolidating these instead of renaming
                    # target = work_orders.filter(name=work_order.name)
                    # units
                    # test_sequence_definition
                    work_order.project = project
                    work_order.save()
            if project.sfdc_number == None:
                project.sfdc_number = obsolete.sfdc_number
            if project.start_date == None:
                project.start_date = obsolete.start_date
            if project.invoice_date == None:
                project.invoice_date = obsolete.invoice_date
            if project.proposal_price == None:
                project.proposal_price = obsolete.proposal_price

            # HERE:
            #     for unit_type in obsolete.unittype_set.all():
            #         unit_type.manufacturer = customer
            #         unit_type.save()
            #     for crate in obsolete.crate_set.all():
            #         crate.shipped_by = customer
            #         crate.save()
            #     for project in obsolete.project_set.all():
            #         project.customer = customer
            #         project.save()
            for oid in PlexusImport.objects.filter(lsdb_id=params.get('id'), lsdb_model='project'):
                oid.lsdb_id = project.id
                oid.save()
            project.save()
            obsolete.delete()
        serializer = ProjectDetailSerializer(project, many=False, context=self.context)
        return Response(serializer.data)

    @action(detail=True, methods=['get'],
            permission_classes=(ConfiguredPermission,),
            serializer_class=WorkOrderProjectSerializer)
    def work_orders(self, request, pk=None):
        """
        This action allows the project managers to list all their project's work orders
        """
        self.context = {'request': request}
        work_orders = Project.objects.get(id=pk).workorder_set.all()
        serializer = self.serializer_class(work_orders, many=True, context=self.context)
        return Response(serializer.data)

    @action(detail=False, methods=['get'],
            permission_classes=(ConfiguredPermission,),
            serializer_class=ProjectSerializer)
    def my_projects(self, request, pk=None):
        """
        This action allows the project managers to list all "active" projects that are "theirs"
        Adding a `?show_archived=true` query parameter on GET will disable the active filter.
        The value can equal any string, I only test for the presence of the parameter.
        """
        self.context = {'request': request}
        show_archived = request.query_params.get('show_archived', 'TRUE')
        if show_archived.upper() == 'TRUE':
            projects = Project.objects.filter(project_manager=request.user)
        else:
            projects = Project.objects.filter(project_manager=request.user, disposition__complete=False)
        serializer = self.serializer_class(projects, many=True, context=self.context)
        return Response(serializer.data)

    @action(detail=False, methods=['get'],
            permission_classes=(ConfiguredPermission,),
            serializer_class=GetActiveProjectsDataGridSerializer)
    def active_projects(self, request, pk=None):
        """
        This action allows all interested parties dig into active project status.
        adding a `?show_archived=true` query parameter on GET will disable the active filter.
        The value can equal any string, I only test for the presence of the parameter.
        """
        self.context = {'request': request}
        show_archived = request.query_params.get('show_archived', 'TRUE')
        if show_archived.upper() == 'TRUE':
            projects = Project.objects.all()
        else:
            projects = Project.objects.filter(disposition__complete=False)
        serializer = self.serializer_class(projects, many=True, context=self.context)
        return Response(serializer.data)

    @transaction.atomic
    @action(detail=True, methods=['get', 'post'],
            serializer_class=ProjectSerializer,
            )
    def link_files(self, request, pk=None):
        """
        This action will link an existing AzureFile to this measurement_result.
        POST: {"id":1} to link azurfefile id=1 to this measurement_result
        """
        self.context = {'request': request}
        queryset = Project.objects.get(id=pk)
        if request.method == 'POST':
            params = request.data
            file_id = params.get('id')
            if file_id:
                attachment = AzureFile.objects.get(id=int(file_id))
                queryset.attachments.add(attachment)
                queryset.save()
        serializer = ProjectSerializer(queryset, many=False, context=self.context)
        return Response(serializer.data)

    @action(detail=True, methods=['get'],
            serializer_class=ProjectSerializer,
            )
    def pi_summary_table(self, request, pk=None):
        table = {
            "project_percent_complete": 0.0,
            "project_time_total": 0.0,
            "project_time_complete": 0.0,
            "work_orders": {}
        }

        project = Project.objects.get(id=pk)
        units_total = 0

        for work_order in project.workorder_set.all():
            work_order_units = 0
            temp_work_order = {
                "name": work_order.name,
                "work_order_percent_complete": 0.0,
                "start_datetime": work_order.start_datetime,
                "operational_efficiency": 0.0,
                "test_sequence_definitions": {}
            }
            time_complete = 0.0
            work_order_units = 0

            time_between = 0

            if temp_work_order["start_datetime"] == None:
                pass
            else:
                time_between = ((timezone.now() - temp_work_order["start_datetime"]).total_seconds() / 60)

            for unit in work_order.units.all():
                if unit.procedureresult_set.last() != None:
                    assigned_name = unit.procedureresult_set.last().test_sequence_definition.short_name
                else:
                    assigned_name = None

                if assigned_name != None and temp_work_order["test_sequence_definitions"].get(assigned_name) != None:
                    temp_tsd = temp_work_order["test_sequence_definitions"][assigned_name]
                elif assigned_name == None:
                    continue
                else:
                    temp_tsd = {
                        "units": 0,
                        "percent_complete": 0.0,
                        "last_action_datetime": None,
                        "operational_efficiency": 0.0,
                        "name": assigned_name
                    }

                (total, completed_minutes) = unit_minutes(unit)

                if assigned_name != None:
                    temp_tsd["units"] += 1
                    if total:
                        temp_tsd["percent_complete"] += 100 * completed_minutes / total
                        temp_tsd["operational_efficiency"] += completed_minutes
                    temp_work_order["test_sequence_definitions"][assigned_name] = temp_tsd

                work_order_units += 1
                units_total += 1
                time_complete += completed_minutes
                if total:
                    temp_work_order["work_order_percent_complete"] += 100 * completed_minutes / total
                    table["project_time_complete"] += completed_minutes
                    table["project_time_total"] += total
            if work_order_units != 0:
                temp_work_order["work_order_percent_complete"] = temp_work_order[
                                                                     "work_order_percent_complete"] / work_order_units
            else:
                temp_work_order["work_order_percent_complete"] = 0

            if temp_work_order["start_datetime"] == None:
                temp_work_order["operational_efficiency"] = 0.0
            else:
                temp_work_order["operational_efficiency"] = 100 * (time_complete / time_between)

            measurements = MeasurementResult.objects.filter(step_result__procedure_result__work_order=work_order)
            for id, tsd in temp_work_order["test_sequence_definitions"].items():
                temp_measurements = measurements.filter(
                    step_result__procedure_result__test_sequence_definition__short_name__iexact=tsd["name"])
                last_action_date = temp_measurements.order_by("date_time").first()

                if last_action_date.date_time:
                    temp_work_order["test_sequence_definitions"][id]["last_action_datetime"] = int(
                        (timezone.now() - last_action_date.date_time).total_seconds() / 60 / 60 / 24)

                if temp_work_order["test_sequence_definitions"][id]["units"]:
                    temp_work_order["test_sequence_definitions"][id]["percent_complete"] = \
                        temp_work_order["test_sequence_definitions"][id]["percent_complete"] / \
                        temp_work_order["test_sequence_definitions"][id]["units"]
                if time_between:
                    temp_work_order["test_sequence_definitions"][id]["operational_efficiency"] = 100 * (
                            temp_work_order["test_sequence_definitions"][id][
                                "operational_efficiency"] / time_between)
                else:
                    temp_work_order["test_sequence_definitions"][id]["operational_efficiency"] = 0

            table["work_orders"][work_order.id] = temp_work_order
        if units_total != 0 and table["project_time_total"] != 0:
            table["project_percent_complete"] = 100 * table["project_time_complete"] / table["project_time_total"]
        else:
            table["project_percent_complete"] = 0

        return Response(table)

    @action(detail=True, methods=['get'],
            serializer_class=ProjectSerializer,
            )
    def burndown_graph(self, request, pk=None):
        """
        This action reports the amount of remaining work (in minutes) a project has each day for the last thirty days.
        The return object is structured as such:
        {
            {
                "id":"Remaining Actual Work",
                "data":[
                    {
                        "x": date
                        "y": Total Time for Project
                    }, ...
                ]
            },
            {
                "id":"Remaining Work",
                "data":[
                    {
                        "x": date
                        "y": Total Time - Completed Time for Date
                    }, ...
                ]
            },
            {
                "id":"Baseline Remaining Work",
                "data":[
                    {
                        "x": date
                        "y": 0
                    }, ...
                ]
            },
        }


        Steps required for this Action:
            - Determine Time Range (Now Through 30 Days ago)
            - Determine aggregate duration for entire project
            - For each day:
                - For each unit:
                    - Determine all procedures done on the day
                    - Determine the highest LEG of the completed procedures (done_to)
                    - Determine time_remaining (completed_time - total_time)
                - Aggregate time_remaining for all units

        """
        self.context = {'request': request}
        end_datetime = timezone.now()
        start_date = end_datetime - datetime.timedelta(days=91)
        delta = datetime.timedelta(days=7)
        graph = [
            {
                "id": "Remaining Actual Work",
                "data": []
            },
            {
                "id": "Remaining Work",
                "data": []
            },
            {
                "id": "Baseline Remaining Work",
                "data": []
            },
            {
                "id": "Test Time",
                "data": []
            }
        ]

        project = Project.objects.get(id=pk)
        units = project.units.all()
        total_time = units.annotate(
            aggregate_time=Sum("procedureresult__procedure_definition__aggregate_duration", filter=(
                                                                                                           Q(procedureresult__supersede=False) | Q(
                                                                                                       procedureresult__supersede__isnull=True)) & (
                                                                                                           Q(procedureresult__procedure_definition__group__name__iexact='Characterizations') | Q(
                                                                                                       procedureresult__procedure_definition__group__name__iexact='Stressors'))),
        ).aggregate(total=Sum("aggregate_time")).get('total') / 60

        while start_date < end_datetime:
            completed_time = 0
            test_time = 0
            for unit in units:
                queryset = unit.procedureresult_set.exclude(supersede=True,
                                                            procedure_definition__group__name__iexact='calibration')

                if queryset.filter(unit__procedureresult__disposition__isnull=False).count() == 0:
                    continue

                done_to = queryset.all().annotate(done_to=Max('unit__procedureresult__linear_execution_group',
                                                              filter=Q(
                                                                  unit__procedureresult__disposition__isnull=False) & Q(
                                                                  unit__procedureresult__stepresult__measurementresult__date_time__range=[
                                                                      "2011-01-01", start_date]))) \
                    .distinct().first()

                if done_to and done_to.done_to:
                    done_to = done_to.done_to
                    minutes_past = queryset.filter(linear_execution_group__lt=done_to) \
                        .exclude(disposition__name__iexact='in progress') \
                        .aggregate(total=Sum('procedure_definition__aggregate_duration')).get('total')

                    minutes_done = queryset.filter(linear_execution_group=done_to) \
                        .exclude(disposition__isnull=True) \
                        .exclude(disposition__name__iexact='in progress') \
                        .aggregate(total=Sum('procedure_definition__aggregate_duration')).get('total')

                else:
                    minutes_done = 0
                    minutes_past = 0
                progress_minutes = queryset.filter(disposition__name__iexact='in progress') \
                    .values('procedure_definition__aggregate_duration', 'start_datetime').first()
                if progress_minutes == None:
                    progress_minutes = 0
                    elapsed = 0
                else:
                    elapsed = min(
                        (timezone.now() - progress_minutes.get('start_datetime')).total_seconds() / 60
                        , progress_minutes.get('procedure_definition__aggregate_duration'))
                if minutes_done == None: minutes_done = 0
                if minutes_past == None: minutes_past = 0

                completed_time += minutes_done + minutes_past + elapsed

            graph[0]["data"].append({
                "x": datetime.date(start_date.year, start_date.month, start_date.day),
                "y": total_time
            })

            graph[1]["data"].append({
                "x": datetime.date(start_date.year, start_date.month, start_date.day),
                "y": total_time - (completed_time / 60)
            })

            graph[2]["data"].append({
                "x": datetime.date(start_date.year, start_date.month, start_date.day),
                "y": 0
            })

            start_date += delta
        # .aggregate(total=Sum('aggregate_time')).get('total')
        return Response(graph)

    @action(detail=True, methods=['get'],
            serializer_class=ProjectSerializer,
            )
    def gantt_graph(self, request, pk=None):
        project = Project.objects.get(id=pk)

        data = []

        for work_order in project.workorder_set.all():

            data_set = [
                [
                    {"type": 'string', "label": 'Task ID'},
                    {"type": 'string', "label": 'Task Name'},
                    {"type": 'string', "label": 'Resource'},
                    {"type": 'date', "label": 'Start Date'},
                    {"type": 'date', "label": 'End Date'},
                    {"type": 'number', "label": 'Duration'},
                    {"type": 'number', "label": 'Percent Complete'},
                    {"type": 'string', "label": 'Dependencies'},
                ]
            ]

            for unit in work_order.units.all():
                queryset = unit.procedureresult_set.exclude(supersede=True,
                                                            procedure_definition__group__name__iexact='calibration')

                backlog_minutes = 0
                frontlog_minutes = 0
                dependency = ""

                temp = queryset.all().annotate(
                    first_date=Min('unit__procedureresult__stepresult__measurementresult__date_time',
                                   filter=Q(unit__procedureresult__disposition__isnull=False)),
                    last_date=Max('unit__procedureresult__stepresult__measurementresult__date_time',
                                  filter=Q(unit__procedureresult__disposition__isnull=False)),
                    done_to=Max('unit__procedureresult__linear_execution_group',
                                filter=Q(unit__procedureresult__disposition__isnull=False)),
                    max_leg=Max('unit__procedureresult__linear_execution_group')
                ) \
                    .distinct().first()
                if temp:
                    (total, completed_minutes) = unit_minutes(unit)
                    if temp.first_date == None:
                        data_set.append([
                            "{}".format(unit.serial_number),
                            "{}".format(unit.serial_number),
                            "{}".format(unit.serial_number),
                            timezone.now(),
                            timezone.now() + datetime.timedelta(minutes=total),
                            total * 60 * 1000,
                            0,
                            None
                        ])
                        continue
                    else:
                        temp_data = []
                        # ToDo: This should use Set of LEG numbers rather than range - MD - MAD - MATTHEW A. DAVIS
                        for leg in range(1, int(temp.max_leg) + 1):
                            temp_set = queryset.filter(linear_execution_group=float(leg)).annotate(
                                first_date=Min('stepresult__measurementresult__date_time'),
                                last_date=Max('stepresult__measurementresult__date_time')
                            )
                            dates = {
                                "first_date": temp_set.order_by('first_date').first().first_date,
                                "last_date": temp_set.order_by(F('last_date').desc(nulls_last=True)).first().last_date
                            }

                            if dates['first_date'] == None and leg <= temp.done_to:
                                backlog_minutes += temp_set.all().aggregate(
                                    total=Sum('procedure_definition__aggregate_duration')).get('total')
                            elif dates['first_date'] == None and leg > temp.done_to:
                                temp_minutes = temp_set.all().aggregate(
                                    total=Sum('procedure_definition__aggregate_duration')).get('total')
                                temp_data.append([
                                    "LEG-{}-{}".format(leg, unit.serial_number),
                                    "{}".format(temp_set.first().name),
                                    "{}".format(unit.serial_number),
                                    temp.last_date + datetime.timedelta(minutes=frontlog_minutes),
                                    temp.last_date + datetime.timedelta(minutes=(frontlog_minutes + temp_minutes)),
                                    temp_minutes * 60 * 1000,
                                    0,
                                    "{}".format(dependency)
                                ])
                                dependency = "LEG-{}-{}".format(leg, unit.serial_number)
                                frontlog_minutes += temp_minutes
                            elif dates['first_date']:
                                temp_minutes = temp_set.all().aggregate(
                                    total=Sum('procedure_definition__aggregate_duration')).get('total')
                                if dates['last_date'] == dates['first_date'] or (
                                        (dates['last_date'] - dates['first_date']).total_seconds() / 60) < temp_minutes:
                                    temp_data.append([
                                        "LEG-{}-{}".format(leg, unit.serial_number),
                                        "{}".format(temp_set.first().name),
                                        "{}".format(unit.serial_number),
                                        temp.first_date,
                                        temp.first_date + datetime.timedelta(minutes=(temp_minutes)),
                                        temp_minutes * 60 * 1000,
                                        max(1, min(100, (temp_minutes / (
                                                (timezone.now() - temp.first_date).total_seconds() / 60) * 100))),
                                        "{}".format(dependency)
                                    ])
                                    dependency = "LEG-{}-{}".format(leg, unit.serial_number)
                                else:
                                    temp_data.append([
                                        "LEG-{}-{}".format(leg, unit.serial_number),
                                        "{}".format(temp_set.first().name),
                                        "{}".format(unit.serial_number),
                                        temp.first_date,
                                        temp.last_date,
                                        (temp.last_date - temp.first_date).total_seconds() * 1000,
                                        100,
                                        "{}".format(dependency)
                                    ])
                                    dependency = "LEG-{}-{}".format(leg, unit.serial_number)

                        temp_data.insert(0, [
                            "{}".format(unit.serial_number),
                            "{}".format(unit.serial_number),
                            "{}".format(unit.serial_number),
                            temp.first_date - datetime.timedelta(minutes=(backlog_minutes)),
                            temp.last_date + datetime.timedelta(minutes=(frontlog_minutes)),
                            total * 60 * 1000,
                            completed_minutes / total * 100,
                            None
                        ])

                        temp_data.insert(1, [
                            "Incomplete".format(leg),
                            "Pre-LSDB Data",
                            "{}".format(unit.serial_number),
                            temp.first_date - datetime.timedelta(minutes=(backlog_minutes)),
                            temp.first_date,
                            backlog_minutes * 60 * 1000,
                            100,
                            None
                        ])
                        print(type(temp.first_date - datetime.timedelta(minutes=(backlog_minutes))))
                        for x in range(len(temp_data)):
                            data_set.append(temp_data[x])
            data.append({"name": work_order.name, "id": work_order.id, "data": data_set})
        return Response(data)
