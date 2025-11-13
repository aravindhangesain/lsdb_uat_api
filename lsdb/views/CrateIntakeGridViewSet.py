from rest_framework import viewsets
from lsdb.models import NewCrateIntake
from lsdb.serializers import CrateIntakeGridSerializer
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

class MyCustomPagination(PageNumberPagination):
    page_size = 20
    def get_paginated_response(self, data):
        return Response(data)
    def to_representation(self, instance):
        return instance

class CrateIntakeGridViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = NewCrateIntake.objects.all()
    serializer_class = CrateIntakeGridSerializer
    pagination_class = MyCustomPagination


