from rest_framework.response import Response
from rest_framework import viewsets
from collections import defaultdict
from lsdb.serializers import GetAllModuleDetailsSerializer, ModulePropertySerializer,ModuleIntakeDetailsSerializer
from lsdb.models import ModuleIntakeImages, Unit, UnitType, ExpectedUnitType,ModuleIntakeDetails

class GetAllModuleDetailsViewSet(viewsets.ModelViewSet):
    queryset = ModuleIntakeImages.objects.all()
    serializer_class = GetAllModuleDetailsSerializer
    lookup_field = 'moduleintake_id'

    def get_queryset(self):
        moduleintake_id = self.kwargs.get(self.lookup_field)
        return ModuleIntakeImages.objects.filter(moduleintake_id=moduleintake_id)
    
    def retrieve(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        moduleintake_id = self.kwargs.get(self.lookup_field)
        if not queryset.exists():
            try:
                module_instance = ModuleIntakeDetails.objects.get(id=moduleintake_id)
            except ModuleIntakeDetails.DoesNotExist:
                return Response({"detail": "Not found."}, status=404)
            data = {
                'module_intake_details': {
                    'moduleintake_id': module_instance.id,
                    'location': module_instance.location_id,
                    'location_name': 'NAPA',
                    'lot_id': module_instance.lot_id,
                    'projects_id': module_instance.projects_id,
                    'project_number': module_instance.projects.number,
                    'customer': module_instance.customer_id,
                    'customer_name': module_instance.customer.name,
                    'manufacturer_name': module_instance.customer.name,
                    'bom': module_instance.bom,
                    'number_of_modules': module_instance.number_of_modules,
                    'steps': module_instance.steps,
                    'is_complete': module_instance.is_complete,
                    'intake_date': module_instance.intake_date,
                    'received_date': module_instance.received_date,
                    'intake_by': module_instance.intake_by,
                    'newcrateintake': module_instance.newcrateintake_id,
                    'crate_name': module_instance.newcrateintake.crate_name
                },
                'scanned_pannel_details': [
                    {
                        'id': panel.id,
                        'serial_number': panel.serial_number,
                        'test_sequence': panel.test_sequence.id if panel.test_sequence else None,
                        'test_sequence_name': panel.test_sequence.name if panel.test_sequence else "No Tests Assigned",
                        'module_type': module_instance.module_type,
                        'status': panel.status,
                        'unit_id': Unit.objects.filter(serial_number=panel.serial_number).values_list('id', flat=True).first()
                    }
                    for panel in module_instance.scannedpannels_set.all()
                ],
                'module_property_details': self.get_module_property_details(module_instance),
                'expected_unit_count': self.get_expected_unit_count(module_instance)
            }
            return Response(data)
        # If queryset is not empty
        intake_instance = queryset.first().moduleintake
        images = queryset.all()
        # Group images by label_name
        categorized_images = defaultdict(list)
        for img in images:
            img_data = {
                'id': img.id,
                'label_name': img.label_name,
                'image_path': f"https://haveblueazdev.blob.core.windows.net/testmedia1/{img.image_path}" if img.image_path else None,
                'notes': img.notes
            }
            categorized_images[img.label_name].append(img_data)
        # Format the categorized images
        categories_of_module_images = [
            {
                'label_name': label_name,
                'images': images
            }
            for label_name, images in categorized_images.items()
        ]
        # Prepare the data for serialization
        data = {
            'module_intake_details': {
                'moduleintake_id': intake_instance.id,
                'location': intake_instance.location_id,
                'location_name': 'NAPA',
                'lot_id': intake_instance.lot_id,
                'projects_id': intake_instance.projects_id,
                'project_number': intake_instance.projects.number,
                'customer': intake_instance.customer_id,
                'customer_name': intake_instance.customer.name,
                'manufacturer_name': intake_instance.customer.name,
                'bom': intake_instance.bom,
                'number_of_modules': intake_instance.number_of_modules,
                'steps': intake_instance.steps,
                'is_complete': intake_instance.is_complete,
                'intake_date': intake_instance.intake_date,
                'received_date': intake_instance.received_date,
                'intake_by': intake_instance.intake_by,
                'newcrateintake': intake_instance.newcrateintake_id,
                'crate_name': intake_instance.newcrateintake.crate_name
            },
            'scanned_pannel_details': [
                {
                    'id': panel.id,
                    'serial_number': panel.serial_number,
                    'test_sequence': panel.test_sequence.id if panel.test_sequence else None,
                    'test_sequence_name': panel.test_sequence.name if panel.test_sequence else "No Tests Assigned",
                    'module_type': intake_instance.module_type,
                    'status': panel.status,
                    'unit_id': Unit.objects.filter(serial_number=panel.serial_number).values_list('id', flat=True).first()
                }
                for panel in intake_instance.scannedpannels_set.all()
            ],
            'module_image_details': [
                {
                    'id': img.id,
                    'label_name': img.label_name,
                    'image_path': f"https://haveblueazdev.blob.core.windows.net/testmedia1/{img.image_path}" if img.image_path else None
                }
                for img in images
            ],
            'categories_of_module_images': categories_of_module_images,
            'module_property_details': self.get_module_property_details(intake_instance),
            'expected_unit_count': self.get_expected_unit_count(intake_instance)
        }
        return Response(data)
    
    def get_module_property_details(self, intake_instance):
        try:
            unit_type = UnitType.objects.get(model=intake_instance.module_type)
            module_property = unit_type.module_property
            if module_property:
                return ModulePropertySerializer(module_property, context=self.get_serializer_context()).data
            else:
                return {}  # Return an empty dictionary if module_property is not found
        except UnitType.DoesNotExist:
            return {}  # Return an empty dictionary if unit_type is not found
        
    def get_expected_unit_count(self, intake_instance):
        try:
            unit_type = UnitType.objects.get(model=intake_instance.module_type)
            expected_unit_type = ExpectedUnitType.objects.filter(unit_type_id=unit_type.id).first()
            return [expected_unit_type.expected_count] if expected_unit_type else []
        except UnitType.DoesNotExist:
            return []