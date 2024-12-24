from rest_framework import serializers
from lsdb.models import ShippingForm,Project,UnitType,ModuleProperty,Unit
from django.contrib.auth.models import User


class ShippingFormSerializer(serializers.ModelSerializer):
    customer_name = serializers.ReadOnlyField(source='customer.name')

    class Meta:
        model=ShippingForm
        fields=[
            'id',
            'factory_name',
            'factory_address',
            'client_name',
            'client_address',
            'client_contactor',
            'client_tel',
            'customer',
            'customer_name',
            'pi_contactor',
            'pi_tel',
            'pi_address'
        ]


class ShippingFormDetailSerializer(serializers.ModelSerializer):
    customer_name = serializers.ReadOnlyField(source='customer.name')
    units = serializers.SerializerMethodField()
    project_number=serializers.SerializerMethodField()
    responsible_staff=serializers.SerializerMethodField()
    shipping_form_data=serializers.SerializerMethodField()

    def get_shipping_form_data(self, obj):
        shipping_form_data = ShippingForm.objects.filter(customer_id=obj.customer).values().first()
        return shipping_form_data if shipping_form_data else None

    def get_responsible_staff(self, obj):
        project_number = self.context.get('project_number', None)
        project_manager_id=Project.objects.filter(number=project_number).values_list('project_manager_id',flat=True).first()
        responsible_staff=User.objects.filter(id=project_manager_id).values_list('username',flat=True).first()
        return responsible_staff


    def get_project_number(self, obj):
        project_number = self.context.get('project_number', None)
        return project_number

    def get_units(self, obj):
        project_number = self.context.get('project_number', None)
        units = []

        if project_number:
            try:
                project = Project.objects.get(number=project_number)
                serial_numbers = project.units.values_list('serial_number', flat=True)
                for serial_number in serial_numbers:
                    unit = Unit.objects.filter(serial_number=serial_number).first()
                    if unit:
                        unit_type = UnitType.objects.filter(id=unit.unit_type_id).first()
                        if unit_type:
                            module_property_id = unit_type.module_property_id
                            nameplate_pmax = ModuleProperty.objects.filter(id=module_property_id).values_list('nameplate_pmax', flat=True).first()
                            units.append({
                                "serial_number": serial_number,
                                "nameplate_pmax": nameplate_pmax
                            })
            except Project.DoesNotExist:
                return []

        return units

    class Meta:
        model = ShippingForm
        fields = [
            'shipping_form_data',
            'customer',
            'customer_name',
            'project_number',
            'responsible_staff',
            'units',
        ]



