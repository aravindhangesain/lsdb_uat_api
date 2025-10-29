from rest_framework import viewsets
from lsdb.serializers import *
from lsdb.models import *
from rest_framework.response import Response
from rest_framework import status


class UserAssignmentForProcedureViewSet(viewsets.ModelViewSet):
    queryset=UserAssignmentForProcedure.objects.all()
    serializer_class=UserAssignmentForProcedureSerializer

    def create(self,request):
        user_ids=request.data.get('user_ids')
        procedure_result_ids=request.data.get('procedure_result_ids')

        for user_id in user_ids:
            for procedure_result_id in procedure_result_ids:
                UserAssignmentForProcedure.objects.create(user_id=user_id,procedure_result_id=procedure_result_id,assigned_by_id=request.user.id)
        return Response({"detail":"Procedure assigned to selected user/users"}, status=status.HTTP_200_OK)
