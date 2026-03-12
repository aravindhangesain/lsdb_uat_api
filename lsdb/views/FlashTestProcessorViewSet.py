import json
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser
from lsdb.utils.FlashTestProcessor import process_flash_test

class FlashTestProcessorViewSet(viewsets.ViewSet):
    parser_classes = [MultiPartParser, FormParser]

    @action(detail=False, methods=["post"])
    def process(self, request):
        uploaded_file = request.FILES.get("file")
        if not uploaded_file:
            return Response({"error": "JSON file is required"},status=status.HTTP_400_BAD_REQUEST)
        try:
            data = json.load(uploaded_file)
            result = process_flash_test(data)
            return Response(result)
        except Exception as e:
            return Response({"error": str(e)},status=status.HTTP_400_BAD_REQUEST)