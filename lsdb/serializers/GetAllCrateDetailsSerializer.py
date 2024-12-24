from rest_framework import serializers
from lsdb.models import CrateIntakeImages, NewCrateIntake
from lsdb.serializers import CrateIntakeImagesSerializer
from collections import defaultdict

class GetAllCrateDetailsSerializer(serializers.ModelSerializer):
    crate_image_details = serializers.SerializerMethodField()
    categories_of_crate_images = serializers.SerializerMethodField()
    customer_name = serializers.ReadOnlyField(source="customer.name")
    manufacturer_name = serializers.ReadOnlyField(source="customer.name")
    project_number  = serializers.ReadOnlyField(source="project.number")

    def get_crate_image_details(self, obj):
        request = self.context.get('request')
        crate_images = CrateIntakeImages.objects.filter(newcrateintake_id=obj.id)
        crate_image_details = CrateIntakeImagesSerializer(crate_images, many=True).data

        for image_detail in crate_image_details:
            if request:
                image_detail['image_path'] = request.build_absolute_uri(image_detail['image_path'])

        return crate_image_details

    def get_categories_of_crate_images(self, obj):
        request = self.context.get('request')
        crate_images = CrateIntakeImages.objects.filter(newcrateintake_id=obj.id)
        crate_image_details = CrateIntakeImagesSerializer(crate_images, many=True).data

        # Group images by label_name
        categorized_images = defaultdict(list)
        for image_detail in crate_image_details:
            if request:
                image_detail['image_path'] = request.build_absolute_uri(image_detail['image_path'])
            label_name = image_detail.get('label_name')
            categorized_images[label_name].append(image_detail)

        # Format the result as a list of dictionaries with label_name as keys
        categorized_images_list = [{"label_name": label, "images": images} for label, images in categorized_images.items()]

        return categorized_images_list

    class Meta:
        model = NewCrateIntake
        fields = [
            "id",
            "customer",
            "customer_name",
            "manufacturer",
            "manufacturer_name",
            "crate_intake_date",
            "project",
            'project_number',
            "created_by",
            "created_on",
            "crate_image_details",
            "categories_of_crate_images",
            'crate_name'
        ]
