from rest_framework import viewsets,status
from lsdb.models import *
from lsdb.serializers import *
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import IntegrityError, transaction

class ReportChecklistNoteViewSet(viewsets.ModelViewSet):
    queryset = ReportChecklistNote.objects.all()
    serializer_class = ReportChecklistNoteSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    # @transaction.atomic
    # @action(detail=True, methods=['post','GET'])
    # def add_checklist_note(self, request,pk=None):
    #     self.context = {'request': request}
    #     params = request.data
    #     try:
    #         existing_note = ReportChecklistNote.objects.get(pk=pk)
    #     except ReportChecklistNote.DoesNotExist:
    #         return Response({"error": f"Note with id {pk} not found."}, status=status.HTTP_404_NOT_FOUND)
    #     try:
    #         report_result_id = ReportResult.objects.get(id=params.get('report'))
    #         checklist_id = request.GET.get('checklist')
    #         checklist_report_id = request.GET.get('checklist_report')   
    #     except (NoteType.DoesNotExist, ReportResult.DoesNotExist) as e:
    #         return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    #     new_note = ReportChecklistNote.objects.create(
    #         user=request.user,
    #         subject=params.get('subject'),
    #         comment=params.get('comment'),
    #         report=report_result_id,
    #         checklist=checklist_id,
    #         checklist_report=checklist_report_id,
    #         parent_note=existing_note
    #     )
    #     new_note.save()
    #     return Response({"status": "note added"}, status=status.HTTP_201_CREATED)


    @transaction.atomic
    @action(detail=True, methods=['post', 'get'])
    def add_comments(self, request, pk=None):
        self.context = {'request': request}
        params = request.data
        try:
            existing_note = ReportChecklistNote.objects.get(pk=pk)
        except ReportChecklistNote.DoesNotExist:
            return Response(
                {"error": f"Note with id {pk} not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        try:
            report_result = ReportResult.objects.get(id=params.get('report'))
            checklist = CheckList.objects.get(id=request.GET.get('checklist'))
            checklist_report = ChecklistReport.objects.get(id=request.GET.get('checklist_report'))
        except (ReportResult.DoesNotExist, CheckList.DoesNotExist, ChecklistReport.DoesNotExist) as e:
            return Response({"error": "Invalid report id"}, status=status.HTTP_400_BAD_REQUEST)
        parent_note = ReportChecklistNote.objects.filter(
            report=report_result,
            checklist=checklist,
            checklist_report=checklist_report
        ).first()
        if not parent_note:
            parent_note = existing_note  
        new_note = ReportChecklistNote.objects.create(
            user=request.user,
            subject='Comment',
            comment=params.get('comment'),
            report=report_result,
            checklist=checklist,
            checklist_report=checklist_report,
            parent_note=parent_note
        )
        return Response({"status": "note added", "note_id": new_note.id}, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'], url_path='by-report')
    def by_checklistreport(self, request):
            report_id = request.query_params.get('report_result_id')
            checklist_id = request.query_params.get('checklist_id')
            checklist_report_id = request.query_params.get('checklist_report_id')
            if not all([report_id, checklist_id, checklist_report_id]):
                return Response({"error": "Missing some parameters"}, status=400)
            notes = self.queryset.filter(report_id=report_id, checklist_id=checklist_id, checklist_report_id=checklist_report_id).order_by('-datetime')
            notes1 = notes.exclude(subject='Comment')
            serializer = self.get_serializer(notes1, many=True)
            return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def get_comments(self, request, pk=None):
        self.context = {'request': request}
        notes = ReportChecklistNote.objects.filter(parent_note_id=pk).order_by("datetime")
        serializer = self.serializer_class(notes, many=True, context=self.context)
        return Response(serializer.data)