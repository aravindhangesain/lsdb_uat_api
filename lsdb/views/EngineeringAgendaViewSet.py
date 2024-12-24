from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from lsdb.models import Note
# from lsdb.permissions import ConfiguredPermission
from lsdb.serializers import EngineeringAgendaSerializer
import csv
from django.http import HttpResponse


class EngineeringAgendaViewSet(viewsets.ModelViewSet):
    logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
    queryset = Note.objects.all()
    serializer_class = EngineeringAgendaSerializer
    # permission_classes = [ConfiguredPermission]

    @action(detail=False, methods=['get'])
    def closed_flags(self, request):
        flags = Note.objects.filter(note_type__id=3, disposition__complete=True).distinct()
        serializer = self.get_serializer(flags, many=True)
        return Response(serializer.data)
    

    @action(detail=False, methods=['get'], url_path='closed_flags/download')
    def download_closed_flags(self, request):
        closed_flags = Note.objects.filter(note_type__id=3, disposition__complete=True).distinct()

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="Closed_Flags.csv"'

        writer = csv.writer(response)

        writer.writerow([
            'ID',
            'Username',
            'Owner Name',
            'Datetime',
            'Subject',
            'Note Type Name',
            'Disposition Name',
            'Disposition Complete',
            'Labels',
        ])

        for flag in closed_flags:
            serializer = EngineeringAgendaSerializer(flag, context={'request': request})
            data = serializer.data

            label_names = ', '.join([label['name'] for label in data.get('labels', [])])

            owner_name = data.get('owner_name', '')

            writer.writerow([
                data['id'],
                data['username'],
                owner_name,
                data['datetime'],
                data['subject'],
                data['note_type_name'],
                data['disposition_name'],
                data['disposition_complete'],
                label_names,
            ])

        return response