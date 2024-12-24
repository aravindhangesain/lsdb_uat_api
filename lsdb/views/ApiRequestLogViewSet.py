from django_filters import rest_framework as filters
from rest_framework_extensions.mixins import DetailSerializerMixin
from rest_framework import viewsets
from rest_framework_tracking.models import APIRequestLog

from lsdb.serializers import ApiRequestLogSerializer
from lsdb.serializers import ApiRequestLogDetailSerializer
from lsdb.permissions import ConfiguredPermission



class LogFilter(filters.FilterSet):
    requested_min = filters.DateFilter(lookup_expr='gte', field_name='requested_at')
    requested_max = filters.DateFilter(lookup_expr='lte', field_name='requested_at')
    # user = filters.RelatedFilter('UserFilter', field_name='user', queryset=User.objects.all())

    class Meta:
        model = APIRequestLog
        fields = [
            'path',
            'status_code',
            'requested_min',
            'requested_max',
        ]

class ApiRequestLogViewSet(DetailSerializerMixin, viewsets.ModelViewSet):
    """
    Filters:
    ?path=
    ?path__icontains=

    requested_at has date range filters:
    `?requested_min=2018-01-01`
    `?requested_max=2018-12-31`
    of course, chain them for a full range: `?requested_min=2021-01-01&requested_max=2021-02-01`
    """
    queryset = APIRequestLog.objects.all()
    serializer_class = ApiRequestLogSerializer
    # permission_classes = [IsSuperUser,]
    serializer_detail_class = ApiRequestLogDetailSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = LogFilter
    permission_classes = [ConfiguredPermission]
