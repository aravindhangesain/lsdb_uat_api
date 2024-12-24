from lsdb.models import ProcedureResult
from rest_framework import viewsets
from lsdb.serializers import verifySerializer
# from lsdb.serializers import UnitDataVerificationSerializer
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination


class MyCustomPagination(PageNumberPagination):
    page_size = 10

    def get_paginated_response(self, data):
        return Response(data)

    def to_representation(self, instance):
        return instance

class ReadOnlyPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        # Allow only GET method
        return request.method == 'GET'


class verifyViewSet(viewsets.ModelViewSet):

    logging_methods = ['GET','POST','PUT','PATCH']
    serializer_class= verifySerializer
    queryset=ProcedureResult.objects.filter(disposition_id=13)
    permission_classes=[ReadOnlyPermission]
    lookup_field='unit_id'
    pagination_class = MyCustomPagination
    

    def retrieve(self, request, *args, **kwargs):
        # Retrieve the value of the lookup field (unit_id)
        unit_id = kwargs.get(self.lookup_field)
        
        # Filter queryset based on the lookup field
        queryset = self.filter_queryset(self.get_queryset()).filter(**{self.lookup_field: unit_id})
        
        # Serialize the queryset
        serializer = self.get_serializer(queryset, many=True)
        
        # Return serialized data
        return Response(serializer.data)
    
    