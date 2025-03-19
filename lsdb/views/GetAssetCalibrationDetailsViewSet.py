from rest_framework import viewsets
from lsdb.models import AssetCalibration
from lsdb.serializers import GetAssetCalibrationDetailsSerializer
from rest_framework import permissions

class ReadOnlyPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.method == 'GET'

class GetAssetCalibrationDetailsViewSet(viewsets.ModelViewSet):
    queryset = AssetCalibration.objects.all()
    serializer_class = GetAssetCalibrationDetailsSerializer
    lookup_field = 'id'
    permission_classes = [ReadOnlyPermission]

    