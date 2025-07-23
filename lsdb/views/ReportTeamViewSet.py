from rest_framework import viewsets
from django.contrib.auth.models import User
from lsdb.models import *
from lsdb.serializers import *
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import connection

class ReportTeamViewSet(viewsets.ModelViewSet):
    queryset = ReportTeam.objects.all()
    serializer_class = ReportTeamSerializer

    @action(detail=False, methods=['get'], url_path='group-users')
    def get_group_users(self, request):
        group_ids = [5, 11]
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT user_id
                FROM lsdb_group_users
                WHERE group_id IN %s
            """, [tuple(group_ids)])
            rows = cursor.fetchall()
        user_ids = [row[0] for row in rows]
        users = User.objects.filter(id__in=user_ids)
        users_map = {user.id: user for user in users}
        final_users = [users_map[uid] for uid in user_ids if uid in users_map]
        serialized = UserSerializer(final_users, many=True, context={'request': request})
        return Response(serialized.data)
    
    @action(detail=False, methods=['get'], url_path='approvers')
    def get_approvers(self, request):
        group_ids = [2,8]
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT user_id
                FROM lsdb_group_users
                WHERE group_id IN %s
            """, [tuple(group_ids)])
            rows = cursor.fetchall()
        user_ids = [row[0] for row in rows]
        users = User.objects.filter(id__in=user_ids)
        users_map = {user.id: user for user in users}
        final_users = [users_map[uid] for uid in user_ids if uid in users_map]
        serialized = UserSerializer(final_users, many=True, context={'request': request})
        return Response(serialized.data)


