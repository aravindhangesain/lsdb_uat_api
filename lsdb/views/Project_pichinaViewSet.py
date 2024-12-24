from rest_framework import viewsets
from lsdb.models import Project_pichina, Workorder_pichina
from rest_framework.decorators import action
from rest_framework.response import Response
from lsdb.permissions import ConfiguredPermission
from lsdb.serializers import GetActiveProjects_pichinaSerializer
from lsdb.serializers import Project_pichinaSerializer
from lsdb.serializers import ProjectDetail_pichinaSerializer
from lsdb.serializers import WorkOrderProject_pichinaSerializer
from lsdb.serializers import WorkorderDataList_pichinaSerializer
from lsdb.utils.ZipFileUtils_pichina import create_download_file
from rest_framework_extensions.mixins import DetailSerializerMixin


class Project_pichinaViewSet(DetailSerializerMixin,viewsets.ModelViewSet):
    logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
    queryset = Project_pichina.objects.all()
    serializer_class = Project_pichinaSerializer
    serializer_detail_class = ProjectDetail_pichinaSerializer
    permission_classes = [ConfiguredPermission]


    @action(detail=False, methods=['get'],
            serializer_class=GetActiveProjects_pichinaSerializer)
    def active_projects(self, request, pk=None):
        self.context = {'request': request}
        show_archived = request.query_params.get('show_archived', 'TRUE')
        if show_archived.upper() == 'TRUE':
            projects = Project_pichina.objects.all()
        else:
            projects = Project_pichina.objects.filter(disposition__complete=False)
        serializer = self.get_serializer(projects, many=True,context={'request': request})
        return Response(serializer.data)
    

    @action(detail=True, methods=['get'])
    def work_orders(self, request, pk=None):
        self.context = {'request': request}
        work_orders = Workorder_pichina.objects.filter(project_id=pk)
        serializer = WorkOrderProject_pichinaSerializer(work_orders, many=True,context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], serializer_class=WorkorderDataList_pichinaSerializer)
    def download(self, request):
        context = {'request': request}
        queryset = Workorder_pichina.objects.all()
        serializer = WorkorderDataList_pichinaSerializer(queryset, many=True, context=context)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'],
            permission_classes=(ConfiguredPermission,),
            serializer_class=WorkorderDataList_pichinaSerializer)
    def download(self, request):
        self.context = {'request': request}
        params = {}
        workorder_ids = request.query_params.get('workorder_ids')
        unit_ids = request.query_params.get('unit_ids')
        procedure_ids = request.query_params.get('procedure_ids')
        TSD_ids = request.query_params.get('test_sequence_definition_ids')
        adjust_images = request.query_params.get('adjust_images')

        str2bool = lambda string: string is not None and string.upper() == 'TRUE'

        if workorder_ids:
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

            queryset = Workorder_pichina.objects.filter(id__in=params["workorder_ids"])

            return create_download_file(work_orders=queryset, tsd_ids=params['test_sequence_definition_ids'],
                                        unit_ids=params['unit_ids'], procedure_ids=params['procedure_ids'],
                                        adjust_images=str2bool(adjust_images))
        else:
            queryset = Workorder_pichina.objects.all()
        serializer = WorkorderDataList_pichinaSerializer(queryset, many=True, context=self.context)
        return Response(serializer.data)


