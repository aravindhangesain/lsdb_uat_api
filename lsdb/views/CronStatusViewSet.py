from rest_framework import viewsets
from django.db.models import Q
from rest_framework.decorators import action
from django.db import connection
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet



class CronStatusViewSet(ViewSet):

    @action(detail=False, methods=['get'])
    def status(self, request):
        with connection.cursor() as cursor:
            # SQL query to check the status
            query = """
                SELECT flag
                FROM cronstatus
                WHERE description = 'Cron job started successfully'
                ORDER BY datetime DESC
                LIMIT 1;
            """
            cursor.execute(query)
            result = cursor.fetchone()

        # Check the flag value in the result
        if result and result[0]:  # If result exists and flag is true
            return Response({'status': True})
        else:
            return Response({'status': False})


