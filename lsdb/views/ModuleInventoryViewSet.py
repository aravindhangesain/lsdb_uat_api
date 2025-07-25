from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
import csv
from django.http import HttpResponse
from rest_framework.decorators import action
from django.utils import timezone
from lsdb.models import Disposition, LocationLog,ScannedPannels,Unit
from lsdb.serializers.ScannedPannelsSerializer import ModuleInventorySerializer,ModuleInventoryDetailSerializer


class ModuleInventoryViewSet(viewsets.ModelViewSet):
    logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
    queryset = ScannedPannels.objects.all()
    serializer_class = ModuleInventorySerializer
    lookup_field = 'serial_number'
    
    def get_queryset(self):
        return self.filter_modules()

    def filter_modules(self):
        serial_number = self.request.query_params.get('serial_number', None)
        project_number = self.request.query_params.get('project_number', None)
        customer = self.request.query_params.get('customer', None)
        location = self.request.query_params.get('location', None)
        active = self.request.query_params.get('active', None)
        queryset = ScannedPannels.objects.all()
        if serial_number:
            queryset = queryset.filter(serial_number=serial_number)
        if project_number:
            queryset = queryset.filter(module_intake__projects__number=project_number)
        if customer:
            queryset = queryset.filter(module_intake__projects__customer__name__icontains=customer)
        if location:
            units = Unit.objects.filter(location__name__icontains=location).values_list('serial_number', flat=True)
            queryset = queryset.filter(serial_number__in=units)
        if active is not None and active.lower() == 'true':
            queryset = queryset.filter(module_intake__projects__disposition__complete=False)
        queryset = queryset.order_by('-module_intake__intake_date')
        return queryset

    def get_serializer_class(self):
        lookup_value = self.kwargs.get(self.lookup_field)
        if lookup_value:
            return ModuleInventoryDetailSerializer
        else:
            return ModuleInventorySerializer
        
    @action(detail=False, methods=['patch'])
    def bulk_eol_disposition_update(self, request):
        serial_numbers = request.data.get('serialNumber')
        eol_disposition = request.data.get('disposition')
        date = request.data.get('date')

        if not serial_numbers:
            return Response({"detail": "Serial numbers are required."}, status=status.HTTP_400_BAD_REQUEST)

        if not isinstance(serial_numbers, list):
            return Response({"detail": "Serial numbers must be a list."}, status=status.HTTP_400_BAD_REQUEST)

        if not eol_disposition and not date:
            return Response({"detail": "At least one of 'disposition' or 'date' must be provided."}, status=status.HTTP_400_BAD_REQUEST)

        for serial_number in serial_numbers:
            scanned_pannels = ScannedPannels.objects.filter(serial_number=serial_number).first()
            if scanned_pannels:
                if eol_disposition is not None:
                    ins=Disposition.objects.get(id=eol_disposition)
                    scanned_pannels.eol_disposition = ins
                if date is not None:
                    scanned_pannels.project_closeout_date = date
                scanned_pannels.save()
            else:
                return Response({"detail": f"Serial number {serial_number} not found."}, status=status.HTTP_404_NOT_FOUND)

        return Response({"detail": "Update successful."}, status=status.HTTP_200_OK)



        


    def update(self, request, *args, **kwargs):
        serial_number = self.kwargs.get(self.lookup_field)
        location = request.data.get('location')
        disposition = request.data.get('eol_disposition')
        arrival_date = request.data.get('arrival_date')
        project_closeout_date = request.data.get('project_closeout_date')
        if not serial_number:
            return Response({"detail": "Serial number is required."}, status=status.HTTP_400_BAD_REQUEST)
        unit_updates = {}
        print(unit_updates)
        scanned_pannels_updates = {}
        if location is not None:
            unit_updates['location'] = location
            print(location)
        if disposition is not None:
            scanned_pannels_updates['eol_disposition_id'] = disposition
        if arrival_date is not None:
            scanned_pannels_updates['arrival_date'] = arrival_date
        if project_closeout_date is not None:
            scanned_pannels_updates['project_closeout_date'] = project_closeout_date
        try:
            if unit_updates:
                unit = Unit.objects.filter(serial_number=serial_number).first()
                if unit:
                    Unit.objects.filter(serial_number=serial_number).update(**unit_updates)
                    if location:
                                if not LocationLog.objects.filter(unit_id=unit.id, location_id=location, is_latest=True).exists():
                                    if LocationLog.objects.filter(unit_id=unit.id).exists():
                                        LocationLog.objects.filter(unit_id=unit.id).update(is_latest=False)
                                        LocationLog.objects.create(location_id=location, unit_id=unit.id, datetime=timezone.now(), flag=3, is_latest=True, username=self.request.user.username)
                                    else:
                                        LocationLog.objects.create(location_id=location, unit_id=unit.id, datetime=timezone.now(), flag=3, is_latest=True, username=self.request.user.username)
                else:
                    return Response({"detail": "Unit not found."}, status=status.HTTP_404_NOT_FOUND)
            if scanned_pannels_updates:
                ScannedPannels.objects.filter(serial_number=serial_number).update(**scanned_pannels_updates)
            return Response({"detail": "Update successful."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    @action(detail=False, methods=['get'], url_path='download_all')
    def download_all(self, request):
        queryset = ScannedPannels.objects.all()
        units = Unit.objects.all()
        unit_locations = {unit.serial_number: unit.location.name for unit in units}
        data = queryset.values(
            'serial_number', 'module_intake__projects__number', 'module_intake__projects__customer__name', 'module_intake__bom',
            'eol_disposition', 'arrival_date', 'project_closeout_date'
        )
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="All_Modules.csv"'
        writer = csv.writer(response)
        writer.writerow(['Serial Number', 'Project Number', 'Customer Name', 'Workorder','Location','EOL Disposition', 'Arrival Date', 'Project Closeout Date'])
        for item in data:
            serial_number = item['serial_number']
            location = unit_locations.get(serial_number, "Unknown")
            writer.writerow([
                serial_number,
                item['module_intake__projects__number'],
                item['module_intake__projects__customer__name'],
                item['module_intake__bom'],
                location,
                item['eol_disposition'],
                item['arrival_date'],
                item['project_closeout_date']
            ])
        return response
    
    @action(detail=False, methods=['get'], url_path='download_active')
    def download_active(self, request):
        queryset1=ScannedPannels.objects.all()
        units= Unit.objects.all()
        queryset =queryset1.filter(module_intake__projects__disposition__complete=False)
        unit_locations = {unit.serial_number: unit.location.name for unit in units}
        data = queryset.values(
            'serial_number',
            'module_intake__projects__number',
            'module_intake__projects__customer__name',
            'module_intake__bom',
            'eol_disposition',
            'arrival_date',
            'project_closeout_date'
        )
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="Active_Modules.csv"'
        writer = csv.writer(response)
        writer.writerow([
            'Serial Number', 'Project Number', 'Customer Name', 'Workorder',
            'Location', 'EOL Disposition', 'Arrival Date', 'Project Closeout Date'
        ])
        for item in data:
            serial_number = item['serial_number']
            location = unit_locations.get(serial_number, "Unknown")
            writer.writerow([
                serial_number,
                item['module_intake__projects__number'],
                item['module_intake__projects__customer__name'],
                item['module_intake__bom'],
                location,
                item['eol_disposition'],
                item['arrival_date'],
                item['project_closeout_date']
            ])
        return response
        
    @action(detail=False, methods=['get'], url_path='download_napa_to_davis')
    def download_napa_to_davis(self, request):
        return self._download_location_csv('Napa to Davis')

    @action(detail=False, methods=['get'], url_path='download_davis_to_napa')
    def download_davis_to_napa(self, request):
        return self._download_location_csv('Davis to Napa')

    def _download_location_csv(self, location_filter):
        units = Unit.objects.filter(location__name__icontains=location_filter)
        unit_locations = {unit.serial_number: unit.location.name for unit in units}
        serial_numbers = list(unit_locations.keys())
        queryset = ScannedPannels.objects.filter(serial_number__in=serial_numbers)
        data = queryset.values(
            'serial_number', 'module_intake__projects__number', 'module_intake__projects__customer__name', 
            'module_intake__bom','eol_disposition', 'arrival_date', 'project_closeout_date'
        )
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="modules_{location_filter.replace(" ", "_").lower()}.csv"'
        writer = csv.writer(response)
        writer.writerow(['Serial Number', 'Project Number', 'Customer Name', 'Workorder','Location','EOL Disposition', 'Arrival Date', 'Project Closeout Date'])
        for item in data:
            serial_number = item['serial_number']
            location = unit_locations.get(serial_number, "Unknown") 
            writer.writerow([
                serial_number,
                item['module_intake__projects__number'],
                item['module_intake__projects__customer__name'],
                item['module_intake__bom'],
                location,
                item['eol_disposition'],
                item['arrival_date'],
                item['project_closeout_date']
            ])
        return response

    @action(detail=False, methods=['get'], url_path='download_csv')
    def download_csv(self, request):
        serial_number = request.query_params.get('serial_number')
        project_number = request.query_params.get('project_number')
        customer = request.query_params.get('customer')
        location = request.query_params.get('location')
        active = request.query_params.get('active')
        queryset = ScannedPannels.objects.all()
        if serial_number:
            queryset = queryset.filter(serial_number=serial_number)
        if project_number:
            queryset = queryset.filter(module_intake__projects__number=project_number)
        if customer:
            queryset = queryset.filter(module_intake__projects__customer__name__icontains=customer)
        if location:
            units = Unit.objects.filter(location__name__icontains=location).values_list('serial_number', flat=True)
            queryset = queryset.filter(serial_number__in=units)
        if active is not None and active.lower() == 'true':
            queryset = queryset.filter(module_intake__projects__disposition__complete=False)
        units = Unit.objects.all()
        unit_locations = {unit.serial_number: unit.location.name if unit.location else "Unknown" for unit in units}
        data = queryset.values(
            'serial_number',
            'module_intake__projects__number',
            'module_intake__projects__customer__name',
            'module_intake__bom',
            'eol_disposition',
            'arrival_date',
            'project_closeout_date'
        )
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="Filtered_Modules.csv"'
        writer = csv.writer(response)
        writer.writerow(['Serial Number', 'Project Number', 'Customer Name', 'Workorder', 'Location', 'EOL Disposition', 'Arrival Date', 'Project Closeout Date'])
        for item in data:
            serial_number = item['serial_number']
            location = unit_locations.get(serial_number, "Unknown") 
            writer.writerow([
                serial_number,
                item['module_intake__projects__number'],
                item['module_intake__projects__customer__name'],
                item['module_intake__bom'],
                location,
                item['eol_disposition'],
                item['arrival_date'],
                item['project_closeout_date']
            ])
        return response