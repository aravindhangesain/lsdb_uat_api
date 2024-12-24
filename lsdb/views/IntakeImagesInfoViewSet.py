from rest_framework import viewsets
from lsdb.models import ModuleIntakeDetails, ScannedPannels
from lsdb.serializers import IntakeImagesInfoSerializer
from rest_framework.exceptions import NotFound
import pandas as pd
from django.http import HttpResponse
from rest_framework.decorators import action
from io import BytesIO

class IntakeImagesInfoViewSet(viewsets.ModelViewSet):
    logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
    queryset = ModuleIntakeDetails.objects.all()
    serializer_class = IntakeImagesInfoSerializer
    pagination_class = None
    lookup_field = 'serial_number'

    def get_object(self):
        serial_number = self.kwargs.get(self.lookup_field)
        
        try:
            scanned_pannel = ScannedPannels.objects.get(serial_number=serial_number)
            obj = ModuleIntakeDetails.objects.get(id=scanned_pannel.module_intake_id)
        except (ScannedPannels.DoesNotExist, ModuleIntakeDetails.DoesNotExist):
            raise NotFound(f"No ModuleIntakeDetails matches the given serial number.")
        self.check_object_permissions(self.request, obj)
        return obj
    
    def get_serializer(self, *args, **kwargs):
        # Ensure that request is included in the context for all serializers
        if 'context' not in kwargs:
            kwargs['context'] = {'request': self.request}
        return super().get_serializer(*args, **kwargs)
    
    @action(detail=False, methods=['get'], url_path='(?P<serial_number>[^/.]+)/download-excel')
    def download_excel(self, request, serial_number=None, *args, **kwargs):
        # Retrieve the specific ModuleIntakeDetails object based on serial number
        try:
            scanned_pannel = ScannedPannels.objects.get(serial_number=serial_number)
            module_intake_detail = ModuleIntakeDetails.objects.get(id=scanned_pannel.module_intake_id)
        except (ScannedPannels.DoesNotExist, ModuleIntakeDetails.DoesNotExist):
            raise NotFound(f"No ModuleIntakeDetails matches the given serial number.")

        # Serialize the data
        serializer = self.get_serializer(module_intake_detail)
        data = serializer.data

        # Create Pandas DataFrames from the data
        module_image_info_df = pd.DataFrame(data['module_image_info'])
        crate_image_info_df = pd.DataFrame(data['crate_image_info'])
        pannel_details_df = pd.DataFrame(data['pannel_details'])
        module_spec_df = pd.DataFrame(data['module_spec'])

        # Create a BytesIO object to write the Excel file to
        output = BytesIO()
        
        # Write the data to the Excel file
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            if not module_image_info_df.empty:
                module_image_info_df.to_excel(writer, index=False, sheet_name='Module Image Info')
            if not crate_image_info_df.empty:
                crate_image_info_df.to_excel(writer, index=False, sheet_name='Crate Image Info')
            if not pannel_details_df.empty:
                pannel_details_df.to_excel(writer, index=False, sheet_name='Pannel Details')
            if not module_spec_df.empty:
                module_spec_df.to_excel(writer, index=False, sheet_name='Module Spec')

        # Seek to the beginning of the stream
        output.seek(0)
        
        # Create the HTTP response with the appropriate Excel content type
        response = HttpResponse(output, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename=module_intake_details.xlsx'
        
        return response
