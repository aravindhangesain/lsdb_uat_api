from rest_framework import viewsets
from lsdb.models import ShippingForm,Project
from lsdb.serializers import ShippingFormSerializer
from lsdb.serializers.ShippingFormSerializer import ShippingFormDetailSerializer
from rest_framework.response import Response


class ShippingFormViewSet(viewsets.ModelViewSet):
    queryset = ShippingForm.objects.all()
    serializer_class = ShippingFormSerializer
    serializer_detail_class = ShippingFormDetailSerializer
    lookup_field='customer'
    
    def get_queryset(self):
        return ShippingForm.objects.all()

    def list(self, request, *args, **kwargs):
        project_number = self.request.query_params.get('project_number')

        if project_number:
            project = Project.objects.filter(number=project_number).first()
            if project:
                context = {'request': request, 'project_number': project_number}
                serializer = self.serializer_detail_class([project], many=True, context=context)
                return Response(serializer.data)
            else:
                return Response({})
        else:
            queryset = self.get_queryset()
            context = {'request': request}
            serializer = self.serializer_class(queryset, many=True, context=context)
            return Response(serializer.data)
    
    def create(self, request):
        customer_id = request.data.get('customer')
        factory_name = request.data.get('factory_name')
        factory_address = request.data.get('factory_address')
        client_name = request.data.get('client_name')
        client_address = request.data.get('client_address')
        client_contactor = request.data.get('client_contactor')
        client_tel = request.data.get('client_tel')
        
        pi_contactor = request.data.get('pi_contactor')
        pi_tel = request.data.get('pi_tel')
        pi_address = request.data.get('pi_address')

        if ShippingForm.objects.filter(customer=customer_id).exists():
            shipping_form = ShippingForm.objects.filter(customer=customer_id).first()
            ShippingForm.objects.filter(id=shipping_form.id).update(
                customer=customer_id if customer_id else shipping_form.customer,
                factory_name=factory_name if factory_name else shipping_form.factory_name,
                factory_address=factory_address if factory_address else shipping_form.factory_address,
                client_name=client_name if client_name else shipping_form.client_name,
                client_address=client_address if client_address else shipping_form.client_address,
                client_contactor=client_contactor if client_contactor else shipping_form.client_contactor,
                client_tel=client_tel if client_tel else shipping_form.client_tel,
                pi_contactor=pi_contactor if pi_contactor else shipping_form.pi_contactor,
                pi_tel=pi_tel if pi_tel else shipping_form.pi_tel,
                pi_address=pi_address if pi_address else shipping_form.pi_address
            )
            updated_form = ShippingForm.objects.get(id=shipping_form.id)
            serializer = self.serializer_class(updated_form, context={'request': request})
            return Response(serializer.data, status=200) 
        else:
            new_form = ShippingForm.objects.create(
                customer_id=customer_id,
                factory_name=factory_name,
                factory_address=factory_address,
                client_name=client_name,
                client_address=client_address,
                client_contactor=client_contactor,
                client_tel=client_tel,
                
                pi_contactor=pi_contactor,
                pi_tel=pi_tel,
                pi_address=pi_address
            )
            serializer = self.serializer_class(new_form, context={'request': request})
            return Response(serializer.data, status=201)