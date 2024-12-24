from rest_framework import serializers
from lsdb.models import ModuleIntakeDetails, ModuleIntakeImages, CrateIntakeImages, ScannedPannels, UnitType, ModuleProperty
from lsdb.serializers import ModuleIntakeImagesSerializer, CrateIntakeImagesSerializer, ScannedPannelsSerializer, ModulePropertySerializer
from collections import defaultdict

class IntakeImagesInfoSerializer(serializers.ModelSerializer):
    module_image_info = serializers.SerializerMethodField()
    categorized_module_images = serializers.SerializerMethodField()
    crate_image_info = serializers.SerializerMethodField()
    categorized_crate_images = serializers.SerializerMethodField()
    pannel_details = serializers.SerializerMethodField()
    module_spec = serializers.SerializerMethodField()

    def get_module_spec(self, obj):
        # Get the first UnitType object that matches the module_type
        module_property_detail = UnitType.objects.filter(model=obj.module_type).first()
        if module_property_detail and module_property_detail.module_property:
            module_details = module_property_detail.module_property.id
            module_spec = ModuleProperty.objects.filter(id=module_details)
            return ModulePropertySerializer(module_spec, many=True, context=self.context).data
        return None

    def get_pannel_details(self,obj):
        scanned_pannels=ScannedPannels.objects.filter(module_intake_id=obj.id)
        return ScannedPannelsSerializer(scanned_pannels, many=True,context=self.context).data
    
    def get_module_image_info(self, obj):
        module_images_info = ModuleIntakeImages.objects.filter(moduleintake_id=obj.id)
        return ModuleIntakeImagesSerializer(module_images_info, many=True,context=self.context).data
    
    def get_categorized_module_images(self, obj):
        module_images_info = ModuleIntakeImages.objects.filter(moduleintake_id=obj.id)
        module_image_details = ModuleIntakeImagesSerializer(module_images_info, many=True,context=self.context).data

        # Group images by label_name
        categorized_images = defaultdict(list)
        for image_detail in module_image_details:
            label_name = image_detail.get('label_name')
            categorized_images[label_name].append(image_detail)

        # Format the result as a list of dictionaries with label_name as keys
        categorized_images_list = [{"label_name": label, "images": images} for label, images in categorized_images.items()]

        return categorized_images_list
    
    def get_crate_image_info(self, obj):
        newcrate_id = obj.newcrateintake_id
        crate_image_info = CrateIntakeImages.objects.filter(newcrateintake_id=newcrate_id)
        return CrateIntakeImagesSerializer(crate_image_info, many=True,context=self.context).data

    def get_categorized_crate_images(self, obj):
        newcrate_id = obj.newcrateintake_id
        crate_image_info = CrateIntakeImages.objects.filter(newcrateintake_id=newcrate_id)
        crate_image_details = CrateIntakeImagesSerializer(crate_image_info, many=True,context=self.context).data

        # Group images by label_name
        categorized_images = defaultdict(list)
        for image_detail in crate_image_details:
            label_name = image_detail.get('label_name')
            categorized_images[label_name].append(image_detail)

        # Format the result as a list of dictionaries with label_name as keys
        categorized_images_list = [{"label_name": label, "images": images} for label, images in categorized_images.items()]

        return categorized_images_list
    
    class Meta:
        model = ModuleIntakeDetails
        fields = [
            'id',
            'module_image_info',
            'categorized_module_images',
            'crate_image_info',
            'categorized_crate_images',
            'pannel_details',
            'module_spec'
        ]
