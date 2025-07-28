from lsdb.models import *
from lsdb.serializers import *
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.db import transaction
from distutils.util import strtobool


class ReportWriterAgendaViewSet(viewsets.ModelViewSet):
    queryset = ReportResult.objects.filter(hex_color='#4ef542')
    serializer_class = ReportWriterAgendaSerializer


    @action(detail=True, methods=["post"])
    def insert_date_time(self, request, pk=None):
        date_time = request.data.get("date_time")
        if not date_time:
            return Response({"error": "tech_writer_start_date is required."}, status=status.HTTP_400_BAD_REQUEST)
        user = request.user
        if not user or not user.is_authenticated:
            return Response({"error": "Authentication required."}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            report_result = ReportResult.objects.get(pk=pk)
        except ReportResult.DoesNotExist:
            return Response({"error": "ReportResult not found."}, status=status.HTTP_404_NOT_FOUND)
        agenda = ReportWriterAgenda.objects.create(
            report_result=report_result,
            tech_writer_start_date=date_time,
            user=user
        )
        serializer = TechWriterStartDateSerializer(agenda)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @transaction.atomic
    @action(detail=False,methods=["post","get"])
    def writer_reviewer_update(self, request):
        if request.method=='POST':
            user_id=request.user.id

            if user_id in [142,103,153]:
                
                report_result_id=request.data.get('report_result_id')

                if report_result_id and report_result_id is not None:
                    
                    reportresult=ReportResult.objects.get(id=report_result_id)

                    reporttype_id=reportresult.report_type_definition.id

                    reportteam=ReportTeam.objects.get(report_type_id=reporttype_id)

                    reviewer_id = request.data.get('reviewer_id')
                    writer_id = request.data.get('writer_id')

                    if reviewer_id:
                        reportteam.reviewer = User.objects.get(id=reviewer_id)

                    if writer_id:
                        reportteam.writer = User.objects.get(id=writer_id)

                    reportteam.save()
                    return Response({"message": "updated successfully"}, status=status.HTTP_200_OK)
                else:
                    return Response({"error": "reportresult_id is required"}, status=status.HTTP_400_BAD_REQUEST)
            
            else:
                return Response({"error": "This user cannot be assigned for this task"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error": "Invalid request method"}, status=status.HTTP_400_BAD_REQUEST)
        
    @transaction.atomic
    @action(detail=False,methods=["post","get"]) 
    def send_to_aprover_grid(self,request):

        flag_raw = request.data.get('flag')
        flag = bool(strtobool(flag_raw)) if flag_raw is not None else None
        report_result_id=request.data.get('report_result_id')

        if flag and report_result_id is not None:
            ReportApproverAgenda.objects.create(flag=flag,report_result_id=report_result_id)
            return Response({"message": "Report Moved to approver grid"}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Invalid payload"}, status=status.HTTP_400_BAD_REQUEST)

            






