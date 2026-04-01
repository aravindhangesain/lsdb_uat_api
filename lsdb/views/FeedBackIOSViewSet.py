from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status, viewsets
from django.db import transaction
from lsdb.models import *
from lsdb.serializers import FeedBackIOSSerializer
from rest_framework.parsers import MultiPartParser, FormParser
import hashlib


class FeedBackIOSViewSet(viewsets.ModelViewSet):
    queryset = FeedBackIOS.objects.all()
    serializer_class = FeedBackIOSSerializer    
        

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        
        azure_file_ids = request.data.get('fb_files', [])

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        feedback = FeedBackIOS.objects.create(
            user=request.user,
            comments=serializer.validated_data.get('comments'),
            fb_type=serializer.validated_data.get('fb_type'),
            priority=serializer.validated_data.get('priority'),
        )

        for file_id in azure_file_ids:

            FeedBackFiles.objects.create(
                feedbackios=feedback,
                azurefile_id=file_id
            )

        serializer = self.get_serializer(feedback, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    

    def get_queryset(self):
        return FeedBackIOS.objects.all()


