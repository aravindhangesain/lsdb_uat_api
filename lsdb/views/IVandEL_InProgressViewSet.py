from django.db.models import Max, Min, Q
from django.db.models.functions import Coalesce
from rest_framework import viewsets
from lsdb.models import ModuleProperty, Unit,ProcedureResult, UnitType
from lsdb.serializers import IVandEL_InProgressSerializer
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny

class IVandEL_InProgressViewSet(viewsets.ModelViewSet):
    queryset = ProcedureResult.objects.all()
    serializer_class = IVandEL_InProgressSerializer
    permission_classes = [AllowAny]
    authentication_classes = []
    
    @action(detail=False, methods=['post'])
    def flash(self, request):
        serial_number = request.data.get("serial_number")
        print("Serial Number:", serial_number)

        # Use filter to avoid MultipleObjectsReturned if serial numbers aren't unique
        units = Unit.objects.filter(serial_number=serial_number)
        unit = units.first()  # Use the first match if there are multiple units

        if not unit:
            return Response("No Procedure Result matches the given serial number.", status=404)

        try:
            unit_type_id = unit.unit_type_id
            module_property_id = UnitType.objects.filter(id=unit_type_id).values_list("module_property_id", flat=True).first()

            if module_property_id is None:
                return Response("No module property found for the given unit type.", status=404)

            bifacial = ModuleProperty.objects.filter(id=module_property_id).values_list("bifacial", flat=True).first()

            procedure_definitions = [14, 54, 50, 62, 33, 49, 21, 38, 48]
            if bifacial is None or not bifacial:
                procedure_definitions.remove(33)

            procedure_results = unit.procedureresult_set.filter(
                Q(disposition__isnull=True) | Q(disposition__complete=False)
            ).exclude(supersede=True).filter(procedure_definition__id__in=procedure_definitions)

            done_to = unit.procedureresult_set.aggregate(
                done_to=Coalesce(
                    Max(
                        "linear_execution_group",
                        filter=Q(
                            disposition__isnull=False,
                            test_sequence_definition__group__name__iexact="sequences",
                            supersede__isnull=True,
                        )
                        | Q(
                            disposition__isnull=False,
                            test_sequence_definition__group__name__iexact="sequences",
                            supersede=False,
                        ),
                    ),
                    0.0,
                )
            ).get("done_to")

            if done_to != 0.0:
                procedure_results = procedure_results.exclude(
                    linear_execution_group__lt=done_to,
                    test_sequence_definition__group__name__iexact="sequences",
                )

            # Aggregate highest leg value
            highest_leg = unit.procedureresult_set.aggregate(
                highest_leg=Coalesce(
                    Min(
                        "linear_execution_group",
                        filter=Q(
                            disposition__isnull=True,
                            linear_execution_group__gt=done_to,
                            allow_skip=False,
                            test_sequence_definition__group__name__iexact="sequences",
                            supersede__isnull=True,
                        )
                        | Q(
                            disposition__isnull=True,
                            allow_skip=False,
                            linear_execution_group__gt=done_to,
                            test_sequence_definition__group__name__iexact="sequences",
                            supersede=False,
                        ),
                    ),
                    99.0,
                )
            ).get("highest_leg")

            procedure_results = procedure_results.exclude(
                linear_execution_group__gt=highest_leg,
                test_sequence_definition__group__name__iexact="sequences",
            )

            procedure_results = list(procedure_results)

            if procedure_results is None:
                return Response("No procedure results found that match the criteria.", status=404)

            # Serialize the procedure result instance
            serializer = IVandEL_InProgressSerializer(procedure_results, many=True, context={"request": request})

            return Response({"status": "success", "data": serializer.data})

        except Exception as e:
            return Response(f"An error occurred: {str(e)}", status=500)


    @action(detail=False, methods=['post'])
    def el(self, request):
        serial_number = request.data.get('serial_number')
        print("Serial Number:", serial_number)
        
        # Use filter to avoid MultipleObjectsReturned if serial numbers aren't unique
        units = Unit.objects.filter(serial_number=serial_number)
        unit = units.first()  # Use the first match if there are multiple units
        
        if not unit:
            return Response("No Procedure Result matches the given serial number.", status=404)

        try:
            procedure_definitions = [12, 18, 37]
            
            # Filter procedure results based on your criteria
            procedure_results = unit.procedureresult_set.filter(
                Q(disposition__isnull=True) | Q(disposition__complete=False)
            ).exclude(supersede=True).filter(procedure_definition__id__in=procedure_definitions)

            # Aggregate done_to value
            done_to = unit.procedureresult_set.aggregate(
                done_to=Coalesce(
                    Max('linear_execution_group',
                        filter=Q(disposition__isnull=False,
                                test_sequence_definition__group__name__iexact='sequences',
                                supersede__isnull=True) | Q(disposition__isnull=False,
                                                            test_sequence_definition__group__name__iexact='sequences',
                                                            supersede=False)
                        ), 0.0)).get('done_to')
            
            if done_to != 0.0:
                procedure_results = procedure_results.exclude(
                    linear_execution_group__lt=done_to,
                    test_sequence_definition__group__name__iexact='sequences'
                )

            # Aggregate highest leg value
            highest_leg = unit.procedureresult_set.aggregate(
                highest_leg=Coalesce(
                    Min('linear_execution_group',
                        filter=Q(disposition__isnull=True,
                                linear_execution_group__gt=done_to,
                                allow_skip=False,
                                test_sequence_definition__group__name__iexact='sequences',
                                supersede__isnull=True) | Q(disposition__isnull=True,
                                                            allow_skip=False,
                                                            linear_execution_group__gt=done_to,
                                                            test_sequence_definition__group__name__iexact='sequences',
                                                            supersede=False)
                        ), 99.0)).get('highest_leg')

            procedure_results = procedure_results.exclude(
                linear_execution_group__gt=highest_leg,
                test_sequence_definition__group__name__iexact='sequences'
            )

            # Retrieve the first matching procedure result
            procedure_result_instance = procedure_results.first()

            if procedure_result_instance is None:
                return Response("No procedure results found that match the criteria.", status=404)

            # Serialize the procedure result instance
            serializer = IVandEL_InProgressSerializer(procedure_result_instance,context={'request': request})

            return Response({'status': 'success', 'data': serializer.data})

        except Exception as e:
            return Response(f"An error occurred: {str(e)}", status=500)
