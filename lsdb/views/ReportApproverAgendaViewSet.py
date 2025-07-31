from rest_framework import viewsets
from lsdb.models import *
from lsdb.serializers import *
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.db import transaction

class ReportApproverAgendaViewSet(viewsets.ModelViewSet):
    queryset = ReportApproverAgenda.objects.filter(flag=True)
    serializer_class = ReportApproverAgendaSerializer
    
    @transaction.atomic
    @action(detail=True, methods=["post"])
    def date_verified(self, request, pk=None):
        date_verified = request.data.get("date_verified")
        if not date_verified:
            return Response({"error": "Approver Date Verification is required."}, status=status.HTTP_400_BAD_REQUEST)
        user = request.user
        if not user or not user.is_authenticated:
            return Response({"error": "Authentication required."}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            report_result = ReportResult.objects.get(pk=pk)
        except ReportResult.DoesNotExist:
            return Response({"error": "ReportResult not found."}, status=status.HTTP_404_NOT_FOUND)
        agenda, created = ReportApproverAgenda.objects.get_or_create(
        report_result=report_result,
        defaults={"date_verified": date_verified, "user": user})
        if not created:
            agenda.date_verified = date_verified
            agenda.save()
            serializer = ReportApproverAgendaSerializer(agenda,context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=["post"])
    def date_approved(self, request, pk=None):
        date_approved = request.data.get("date_approved")
        if not date_approved:
            return Response({"error": "Date Approved Verification is required."}, status=status.HTTP_400_BAD_REQUEST)
        user = request.user
        if not user or not user.is_authenticated:
            return Response({"error": "Authentication required."}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            report_result = ReportResult.objects.get(pk=pk)
        except ReportResult.DoesNotExist:
            return Response({"error": "ReportResult not found."}, status=status.HTTP_404_NOT_FOUND)
        agenda, created = ReportApproverAgenda.objects.get_or_create(
        report_result=report_result,
        defaults={"date_approved": date_approved, "user": user})
        if not created:
            agenda.date_approved = date_approved
            agenda.save()
            serializer = ReportApproverAgendaSerializer(agenda,context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=["post"])
    def date_delivered(self, request, pk=None):
        date_delivered = request.data.get("date_delivered")
        if not date_delivered:
            return Response({"error": "Date Delivered is required."}, status=status.HTTP_400_BAD_REQUEST)
        user = request.user
        if not user or not user.is_authenticated:
            return Response({"error": "Authentication required."}, status=status.HTTP_401_UNAUTHORIZED)
        try:
            report_result = ReportResult.objects.get(pk=pk)
        except ReportResult.DoesNotExist:
            return Response({"error": "ReportResult not found."}, status=status.HTTP_404_NOT_FOUND)
        agenda, created = ReportApproverAgenda.objects.get_or_create(
        report_result=report_result,
        defaults={"date_delivered": date_delivered, "user": user})
        if not created:
            agenda.date_delivered = date_delivered
            agenda.save()
            serializer = ReportApproverAgendaSerializer(agenda,context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
    @transaction.atomic
    @action(detail=False,methods=["post","get"]) 
    def send_to_delivered_grid(self,request):

        
        report_result_id=request.data.get('report_result_id')

        if report_result_id is not None:
            

            reportwritertable=ReportApproverAgenda.objects.get(report_result_id=report_result_id)
            reportwritertable.flag=False
            reportwritertable.save()

            

            return Response({"message": "Report Moved to delivered grid"}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Invalid payload"}, status=status.HTTP_400_BAD_REQUEST)