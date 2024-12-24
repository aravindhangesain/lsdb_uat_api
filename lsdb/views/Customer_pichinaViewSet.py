from rest_framework import viewsets
from lsdb.serializers import Customer_pichinaSerializer
from lsdb.serializers import CustomerDetail_pichinaSerializer
from rest_framework_extensions.mixins import DetailSerializerMixin

from lsdb.models import Customer_pichina


class Customer_pichinaViewSet(DetailSerializerMixin,viewsets.ModelViewSet):
    logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
    queryset = Customer_pichina.objects.all()
    serializer_class = Customer_pichinaSerializer
    serializer_detail_class = CustomerDetail_pichinaSerializer
