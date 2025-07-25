from lsdb.models import *
from lsdb.serializers import *
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

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
