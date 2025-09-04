from rest_framework import viewsets
from lsdb.models import *
from lsdb.serializers import *
from rest_framework.decorators import action
from rest_framework.response import Response

class ProjectdownloadViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectdownloadSerializer
    lookup_field = 'number'

    def retrieve(self, request, number=None):
        project = self.get_object()
        data = {
            "project_id": project.id,
            "project_number": project.number,
            "workorders": []
        }
        for workorder in project.workorder_set.all():
            procedures = ProcedureResult.objects.filter(
                work_order=workorder.id
            ).values('procedure_definition__id','procedure_definition__name','test_sequence_definition__id','test_sequence_definition__name','name').exclude(group_id=45)
            seen = set()
            procedures_list = []
            for proc in procedures:
                pid = proc['procedure_definition__id']
                if pid not in seen:
                    seen.add(pid)
                    procedures_list.append({
                        "procedure_definition_id": pid,
                        "procedure_definition_name": proc['procedure_definition__name']
                    })
            seen_prn = set()
            procedure_result_names = []
            for proc in procedures:
                pname = proc.get('name')
                if pname and pname not in seen_prn:
                    seen_prn.add(pname)
                    procedure_result_names.append(pname)
            # seen_tsd = set()
            # tsd_list = []
            # for tsd in procedures:
            #     tid = tsd['test_sequence_definition__id']
            #     if tid not in seen_tsd:
            #         seen_tsd.add(tid)
            #         tsd_list.append({
            #             "id": tid,
            #             "name": tsd['test_sequence_definition__name']
            #         })
           
            data["workorders"].append({
                "workorder_id": workorder.id,
                "workorder_name": workorder.name,
                "procedure_definitions": procedures_list,
                "procedure_names":procedure_result_names,
                # "test_sequences": tsd_list,
            })
        return Response(data)