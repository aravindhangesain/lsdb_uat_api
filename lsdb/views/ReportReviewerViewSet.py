from rest_framework import viewsets

from lsdb.models import ReportReviewer
from lsdb.serializers import ReportReviewerSerializer

class ReportReviewerViewSet(viewsets.ModelViewSet):
    queryset = ReportReviewer.objects.all()
    serializer_class = ReportReviewerSerializer