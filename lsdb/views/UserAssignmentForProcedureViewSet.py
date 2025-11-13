from rest_framework import viewsets
from lsdb.serializers import *
from lsdb.models import *
from rest_framework.response import Response
from rest_framework import status
from django_filters import rest_framework as filters
from rest_framework.decorators import action
from django.db import IntegrityError, transaction




class UserAssignmentForProcedureFilter(filters.FilterSet):
    procedure_result = filters.BaseInFilter(field_name='procedure_result', lookup_expr='in')

    class Meta:
        model = UserAssignmentForProcedure
        fields = ['procedure_result']


class UserAssignmentForProcedureViewSet(viewsets.ModelViewSet):
    queryset=UserAssignmentForProcedure.objects.all()
    serializer_class=UserAssignmentForProcedureSerializer
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = UserAssignmentForProcedureFilter

    def create(self,request):
        user_ids=request.data.get('user_ids')
        procedure_result_ids=request.data.get('procedure_result_ids')
        due_on=request.data.get('due_on')

        for user_id in user_ids:
            for procedure_result_id in procedure_result_ids:
                UserAssignmentForProcedure.objects.create(user_id=user_id,procedure_result_id=procedure_result_id,assigned_by_id=request.user.id,due_on=due_on)
        return Response({"detail":"Procedure assigned to selected user/users"}, status=status.HTTP_200_OK)
    
    @transaction.atomic
    @action(detail=False, methods=['post'])
    def update_user_assignments(self, request):
        """
        Body: { procedure_result_id:1,"user_ids": [153,123] }
        """
        procedure_result_id = request.data.get('procedure_result_id')
        user_ids = request.data.get('user_ids',[])
        due_on=request.data.get('due_on')

        if not procedure_result_id:
            return Response(
                {"detail": "Missing 'procedure_result' query parameter."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not user_ids:
            return Response(
                {"detail": "Missing 'user_id' in request body."},
                status=status.HTTP_400_BAD_REQUEST
            )
        UserAssignmentForProcedure.objects.filter(procedure_result_id=procedure_result_id).delete()
        
        for user_id in user_ids:
            UserAssignmentForProcedure.objects.create(user_id=user_id,procedure_result_id=procedure_result_id,assigned_by_id=request.user.id,due_on=due_on)
       

        return Response(
            {"detail": f"Updated procedures assigned users "},
            status=status.HTTP_200_OK
        )