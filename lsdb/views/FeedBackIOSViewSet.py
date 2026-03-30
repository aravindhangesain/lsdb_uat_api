from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status, viewsets
from django.db import transaction
from lsdb.models import *
from lsdb.serializers import FeedBackIOSSerializer


class FeedBackIOSViewSet(viewsets.ModelViewSet):
    queryset = FeedBackIOS.objects.all()
    serializer_class = FeedBackIOSSerializer

    def create(self, request, *args, **kwargs):
        
        file = request.FILES.get('fb_file')

        if not file:
            return Response(
                {"error": "File is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        azure_file = AzureFile.objects.create(file=file,length=file.size)

        feedback = FeedBackIOS.objects.create(
            user=request.user,
            fb_file=azure_file,
            comments=serializer.validated_data.get('comments'),
            fb_type=serializer.validated_data.get('fb_type'),
            priority=serializer.validated_data.get('priority'),
        )

        output_serializer = self.get_serializer(feedback)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)
        
    def get_queryset(self):
        return FeedBackIOS.objects.all()


