import json
from rest_framework import viewsets,status
from lsdb.models import *
from lsdb.serializers import *
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import IntegrityError, transaction


class ReportNotesViewSet(viewsets.ModelViewSet):
    queryset = ReportNotes.objects.all()
    serializer_class = ReportNotesSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'], url_path='by-report')
    def by_report(self, request):
        report_id = request.query_params.get('report_id')
        if not report_id:
            return Response({"error": "Missing report_id in query parameters"}, status=400)
        notes = self.queryset.filter(report_id=report_id)
        serializer = self.get_serializer(notes, many=True)
        return Response(serializer.data)
    
    @transaction.atomic
    @action(detail=True, methods=['post'])
    def add_note(self, request,pk=None):
        self.context = {'request': request}
        params = request.data
        try:
            existing_note = ReportNotes.objects.get(pk=pk)
        except ReportNotes.DoesNotExist:
            return Response({"error": f"Note with id {pk} not found."}, status=status.HTTP_404_NOT_FOUND)
        if params.get('reviewer'):
            reviewer = ReportReviewer.objects.get(id=params.get('reviewer'))
            existing_note.reviewer = reviewer
            existing_note.save()
        note_type = NoteType.objects.get(id=params.get('type'))
        report = ReportResult.objects.get(id=params.get('report'))
        reviewer = ReportReviewer.objects.get(id=params.get('reviewer'))
        new_note = ReportNotes.objects.create(
            user=request.user,
            subject=params.get('subject'),
            comment=params.get('comment'),
            type=note_type,
            reviewer=reviewer,
            report=report,
            parent_note=existing_note
        )
        if note_type.id in [1,3]:
            for label_id in params.get('labels', []):
                ReportNoteLabels.objects.create(reportnote=new_note, label_id=label_id)
            for user_id in params.get('tagged_users', []):
                ReportNoteTaggedPM.objects.create(reportnote=new_note, project_manager_id=user_id)
        else:
            new_note.labels.set(params.get('labels', []))
            new_note.tagged_users.set(params.get('tagged_users', []))
        new_note.save()
        return Response({"status": "note added"}, status=status.HTTP_201_CREATED)
    
    @transaction.atomic
    @action(detail=False, methods=['post'])
    def add_flag(self, request):
        self.context = {'request': request}
        params = request.data
        # try:
        #     existing_note = ReportNotes.objects.get(pk=pk)
        # except ReportNotes.DoesNotExist:
        #     return Response({"error": f"Note with id {pk} not found."}, status=status.HTTP_404_NOT_FOUND)
        # if params.get('reviewer'):
        #     reviewer = ReportReviewer.objects.get(id=params.get('reviewer'))
        #     existing_note.reviewer = reviewer
        #     existing_note.save()
        note_type = NoteType.objects.get(id=params.get('type'))
        report = ReportResult.objects.get(id=params.get('report'))
        reviewer = ReportReviewer.objects.get(id=params.get('reviewer'))
        new_note = ReportNotes.objects.create(
            user=request.user,
            subject=params.get('subject'),
            comment=params.get('comment'),
            type=note_type,
            reviewer=reviewer,
            report=report
            # parent_note=existing_note
        )
        if note_type.id in [1, 3]:
            for label_id in params.get('labels', []):
                ReportNoteLabels.objects.create(reportnote=new_note, label_id=label_id)
            for user_id in params.get('tagged_users', []):
                ReportNoteTaggedPM.objects.create(reportnote=new_note, project_manager_id=user_id)
        else:
            new_note.labels.set(params.get('labels', []))
            new_note.tagged_users.set(params.get('tagged_users', []))
        new_note.save()
        return Response({"status": "note or flag added"}, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['get'])
    def get_children(self, request, pk=None):
        self.context = {'request': request}
        notes = ReportNotes.objects.filter(parent_note__id=pk).order_by("datetime")
        serializer = self.serializer_class(notes, many=True, context=self.context)
        return Response(serializer.data)
