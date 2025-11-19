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
            # 1. Get latest "Cron job started successfully"
            query_started = """
                SELECT flag
                FROM cronstatus
                WHERE description = 'Cron job started successfully'
                ORDER BY datetime DESC
                LIMIT 1;
            """
            cursor.execute(query_started)
            result_started = cursor.fetchone()

            # If started flag is false, fetch latest ended datetime
            if not result_started or not result_started[0]:
                query_ended = """
                    SELECT datetime
                    FROM cronstatus
                    WHERE description = 'Cron job ended successfully'
                    ORDER BY datetime DESC
                    LIMIT 1;
                """
                cursor.execute(query_ended)
                last_end = cursor.fetchone()

                return Response({
                    'status': False,
                    'datetime': last_end[0] if last_end else None
                })

        # If flag is true, return True
        return Response({'status': True})


