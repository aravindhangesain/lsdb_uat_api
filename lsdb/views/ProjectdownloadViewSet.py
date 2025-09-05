from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from lsdb.models import *
from lsdb.serializers import *
from rest_framework.decorators import action
from rest_framework.response import Response
from django.http import HttpResponse
from django.utils import timezone
import zipfile
from io import BytesIO
from openpyxl import Workbook
from PIL import Image, ImageOps

class ProjectdownloadViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectdownloadSerializer
    lookup_field = 'number'

    def retrieve(self, request, number=None):
        project = self.get_object()
        data = {
            "project_id": project.id,
            "project_number": project.number,
            "workorders": []
        }
        for workorder in project.workorder_set.all():
            procedures = ProcedureResult.objects.filter(
                work_order=workorder.id
            ).values('procedure_definition__id','procedure_definition__name','test_sequence_definition__id','test_sequence_definition__name','name').exclude(group_id=45)
            seen = set()
            procedures_list = []
            for proc in procedures:
                pid = proc['procedure_definition__id']
                if pid not in seen:
                    seen.add(pid)
                    procedures_list.append({
                        "procedure_definition_id": pid,
                        "procedure_definition_name": proc['procedure_definition__name']
                    })
            seen_prn = set()
            procedure_result_names = []
            for proc in procedures:
                pname = proc.get('name')
                if pname and pname not in seen_prn:
                    seen_prn.add(pname)
                    procedure_result_names.append(pname)
            # seen_tsd = set()
            # tsd_list = []
            # for tsd in procedures:
            #     tid = tsd['test_sequence_definition__id']
            #     if tid not in seen_tsd:
            #         seen_tsd.add(tid)
            #         tsd_list.append({
            #             "id": tid,
            #             "name": tsd['test_sequence_definition__name']
            #         })
           
            data["workorders"].append({
                "workorder_id": workorder.id,
                "workorder_name": workorder.name,
                "procedure_definitions": procedures_list,
                "procedure_names":procedure_result_names,
                # "test_sequences": tsd_list,
            })
        return Response(data)
    
    # @action(detail=True, methods=['get'], url_path='download')
    # def download(self, request, number=None):
    #     """
    #     Endpoint: /api/1.0/projectdownload/<pk>/download/
    #     Query Params: procedure_definition_id, procedure_name
    #     """
    #     workorder_id = request.GET.get('workorder_id')
    #     procedure_definition_id = request.GET.get('procedure_definition_id')
    #     procedure_name = request.GET.get('procedure_name')
    #     if not workorder_id:
    #         return Response({"error": "workorder_id is required"}, status=400)
    #     project = get_object_or_404(Project, number=number)
    #     work_order = get_object_or_404(project.workorder_set, id=workorder_id)
        
    #     excel_file_units = Workbook()
    #     unit_sheet = excel_file_units.active
    #     unit_sheet.title = "Units"
    #     unit_sheet.append([
    #         "Manufacturer", "Model",
    #         "Serial Number",
    #         "Maximum Voltage[V]", "Width [mm]", "Height [mm]",
    #         "Pmax [W]", "VOC [V]", "VMP[V]",
    #         "ISC [A]", "IMP [A]", "final_result"
    #     ])
    #     excel_file_flash = Workbook()
    #     flash_sheet = excel_file_flash.active
    #     flash_sheet.title = "Flash"
    #     flash_sheet.append(
    #         ["Serial Number", "TSD", "LEG", "final_result","Pmp", "Voc", "Vmp", "Isc", "Imp", "Irradiance", "Temperature"])
        
    #     excel_file_vi = Workbook()
    #     vi_sheet = excel_file_vi.active
    #     vi_sheet.title = "Visual Inspection"
    #     vi_sheet.append(["Serial Number", "TSD", "LEG", "final_result", "Defect", "Category", "Notes", "Images:"])

    #     excel_file_el = Workbook()
    #     el_sheet = excel_file_el.active
    #     el_sheet.title = "EL Image"
    #     el_sheet.append(
    #         ["Serial Number", "TSD", "LEG", "final_result","Aperture", "ISO", "Exposure Count", "Injection Current",
    #             "Exposure Time"])

    #     excel_file_wl = Workbook()
    #     wl_sheet = excel_file_wl.active
    #     wl_sheet.title = "Wet Leakage"
    #     wl_sheet.append(["Serial Number", "TSD", "LEG", "final_result","Insulation Resistance", "Passed?", "Test Voltage",
    #                         "Leakage Current", "Current Trip Setpoint", "Water Temperature"])

    #     units = Unit.objects.filter(procedureresult__work_order=work_order).distinct()
    #     for unit in units:
    #         unit_sheet.append([
    #             unit.unit_type.manufacturer.name,
    #             unit.unit_type.model,
    #             unit.serial_number,
    #             unit.unit_type.module_property.system_voltage,
    #             unit.unit_type.module_property.module_width,
    #             unit.unit_type.module_property.module_height,
    #             unit.unit_type.module_property.nameplate_pmax,
    #             unit.unit_type.module_property.voc,
    #             unit.unit_type.module_property.vmp,
    #             unit.unit_type.module_property.isc,
    #             unit.unit_type.module_property.imp
    #         ])
    #         procedure_query = ProcedureResult.objects.filter(
    #             unit=unit,
    #             procedure_definition_id=procedure_definition_id,
    #             name=procedure_name
    #         ).order_by('test_sequence_definition', 'linear_execution_group').select_related('unit').prefetch_related('stepresult_set__measurementresult_set')
    #         if not procedure_query.exists():
    #             continue
            
    #         for test in procedure_query:
    #             final_result = ProcedureResult_FinalResult.objects.filter(procedure_result_id=test.id).values_list('final_result', flat=True).first()
    #             final_result_value = final_result if final_result else 'N/A'
    #             if "I-V" in test.procedure_definition.name:
    #                 for step_result in test.stepresult_set.all().exclude(archived=True):
    #                     data = [unit.serial_number, test.test_sequence_definition.name, test.name, final_result_value]
    #                     flash_sheet.append(data)
    #             elif "Wet Leakage" in test.procedure_definition.name:
    #                     for step_result in test.stepresult_set.all().exclude(archived=True):
    #                         data = [unit.serial_number, test.test_sequence_definition.name, test.name,final_result_value]
    #                         for measurement in step_result.measurementresult_set.all().order_by('report_order'):
    #                             data.append(getattr(measurement, measurement.measurement_result_type.name))
    #                         wl_sheet.append(data)
    #             elif "Visual Inspection" in test.procedure_definition.name:
    #                 for step_result in test.stepresult_set.all().exclude(archived=True):
    #                     data = [unit.serial_number, test.test_sequence_definition.name, test.name,final_result_value]
    #                     vi_sheet.append(data)
    #             elif "EL Image" in test.procedure_definition.name:
    #                 for step_result in test.stepresult_set.all().exclude(archived=True):
    #                     data = [unit.serial_number, test.test_sequence_definition.name, test.name,final_result_value]
    #                     el_sheet.append(data)
                
    #     file_stream = BytesIO()
    #     excel_file_units.save(file_stream)
    #     file_stream.seek(0)

    #     mem_zip = BytesIO()
    #     with zipfile.ZipFile(mem_zip, mode='w', compression=zipfile.ZIP_DEFLATED) as zf:
    #         zf.writestr(f'{work_order.name}_{procedure_name}.xlsx', file_stream.read())
    #     filename = timezone.now().strftime('%b-%d-%Y-%H%M%S')
    #     response = HttpResponse(mem_zip.getvalue(), content_type='application/x-zip-compressed')
    #     response['Content-Disposition'] = f'attachment; filename={filename}.zip'
    #     return response


    @action(detail=True, methods=['get'], url_path='download')
    def download(self, request, number=None):
        """
        Endpoint: /api/1.0/projectdownload/<pk>/download/
        Query Params: workorder_id, procedure_definition_id, procedure_name
        """
        workorder_id = request.GET.get('workorder_id')
        procedure_definition_id = request.GET.get('procedure_definition_id')
        procedure_name = request.GET.get('procedure_name')
        adjust_images = False  # Set to True to auto-adjust EL images

        if not workorder_id:
            return Response({"error": "workorder_id is required"}, status=400)

        if not procedure_definition_id or not procedure_name:
            return Response({"error": "procedure_definition_id and procedure_name are required"}, status=400)

        project = get_object_or_404(Project, number=number)
        work_order = get_object_or_404(project.workorder_set, id=workorder_id)

        # Get the procedure definition from DB
        procedure_def = get_object_or_404(ProcedureDefinition, id=procedure_definition_id)

        # Create workbook
        excel_file = Workbook()
        sheet = excel_file.active

        mem_zip = BytesIO()
        with zipfile.ZipFile(mem_zip, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:

            # Helper to sanitize Excel values
            def safe_excel_value(val):
                if hasattr(val, "all"):  # ManyToMany manager
                    return ", ".join(str(v) for v in val.all())
                if isinstance(val, (str, int, float, type(None))):
                    return val
                return str(val)

            # Fetch units linked to this work order (only once)
            units = Unit.objects.filter(procedureresult__work_order=work_order).distinct()

            # I-V Procedure
            if "I-V" in procedure_def.name:
                sheet.title = "Flash"
                sheet.append([
                    "Serial Number", "TSD", "LEG", "final_result",
                    "Pmp", "Voc", "Vmp", "Isc", "Imp", "Irradiance", "Temperature"
                ])

                for unit in units:
                    tests = ProcedureResult.objects.filter(
                        unit=unit,
                        procedure_definition_id=procedure_definition_id,
                        name=procedure_name
                    ).order_by("test_sequence_definition", "linear_execution_group")

                    for test in tests:
                        final_result_value = ProcedureResult_FinalResult.objects.filter(
                            procedure_result_id=test.id
                        ).values_list("final_result", flat=True).first() or "N/A"

                        for step_result in test.stepresult_set.all().exclude(archived=True):
                            data = [
                                safe_excel_value(unit.serial_number),
                                safe_excel_value(test.test_sequence_definition.name),
                                safe_excel_value(test.name),
                                safe_excel_value(final_result_value)
                            ]

                            for measurement in step_result.measurementresult_set.all().order_by("report_order"):

                                # Case 1: Handle flash result files
                                if measurement.measurement_result_type.name == "result_files":
                                    if measurement.result_files.all().count():
                                        has_result = step_result.measurementresult_set.filter(
                                            result_files__name__icontains="Results"
                                        )

                                        for azurefile in measurement.result_files.all():
                                            if has_result and "Results" in azurefile.file.name:
                                                path = "Flash Data/"
                                                if "200" in step_result.name:
                                                    path += "200W/"
                                                elif "Rear" in test.procedure_definition.name:
                                                    path += "Rear/"
                                                path += "FLASH/{}/{}".format(
                                                    test.test_sequence_definition.name,
                                                    test.name
                                                )
                                                file_bytes = azurefile.file.file.read()
                                                zf.writestr(
                                                    "{}/{}/{}/{}/{}".format(
                                                        work_order.project.number,
                                                        work_order.name,
                                                        "Flash Data",
                                                        path,
                                                        azurefile.file.name,
                                                    ),
                                                    file_bytes
                                                )
                                            elif not has_result:
                                                path = "Flash Data/"
                                                if "200" in step_result.name:
                                                    path += "200W/"
                                                elif "Rear" in test.procedure_definition.name:
                                                    path += "Rear/"
                                                path += "FLASH/{}/{}".format(
                                                    test.test_sequence_definition.name,
                                                    test.name
                                                )
                                                file_bytes = azurefile.file.file.read()
                                                zf.writestr(
                                                    "{}/{}/{}/{}/{}".format(
                                                        work_order.project.number,
                                                        work_order.name,
                                                        "Flash Data",
                                                        path,
                                                        azurefile.file.name,
                                                    ),
                                                    file_bytes
                                                )
                                            else:
                                                continue

                                # Case 2: Skip datetime values
                                elif measurement.measurement_result_type.name == "result_datetime":
                                    continue

                                # Case 3: Regular measurement values
                                else:
                                    raw_value = getattr(measurement, measurement.measurement_result_type.name, "")
                                    data.append(safe_excel_value(raw_value))

                            sheet.append(data)


            # Visual Inspection Procedure
            elif "Visual Inspection" in procedure_def.name:
                sheet.title = "Visual Inspection"
                sheet.append([
                    "Serial Number", "TSD", "LEG", "final_result",
                    "Defect", "Category", "Notes", "Images"
                ])

                for unit in units:
                    tests = ProcedureResult.objects.filter(
                        unit=unit,
                        procedure_definition_id=procedure_definition_id,
                        name=procedure_name
                    ).order_by("test_sequence_definition", "linear_execution_group")

                    for test in tests:
                        final_result_value = ProcedureResult_FinalResult.objects.filter(
                            procedure_result_id=test.id
                        ).values_list("final_result", flat=True).first() or "N/A"

                        skip = False
                        for step_result in test.stepresult_set.all().exclude(archived=True):
                            data = [
                                unit.serial_number,
                                safe_excel_value(test.test_sequence_definition.name),
                                safe_excel_value(test.name),
                                safe_excel_value(final_result_value)
                            ]

                            for measurement in step_result.measurementresult_set.all().order_by("report_order"):

                                # Case 1: Inspect Module → skip further defects if clean
                                if step_result.name == "Inspect Module":
                                    if getattr(measurement, measurement.measurement_result_type.name):
                                        skip = True
                                        data.append("No Defects Observed")
                                        sheet.append(data)
                                elif skip:
                                    break

                                # Case 2: Image files → add to ZIP and record filenames
                                elif measurement.measurement_result_type.name == "result_files":
                                    if measurement.result_files.all().count():
                                        for azurefile in measurement.result_files.all():
                                            file_bytes = azurefile.file.file.read()
                                            zf.writestr(
                                                "{}/{}/{}/{}".format(
                                                    work_order.project.number,
                                                    work_order.name,
                                                    "VI Images",
                                                    azurefile.file.name,
                                                ),
                                                file_bytes
                                            )
                                            data.append(azurefile.file.name)

                                # Case 3: Defects → add defect details
                                elif measurement.result_defect is not None and measurement.measurement_result_type.name == "result_defect":
                                    data.append(safe_excel_value(measurement.result_defect.short_name))
                                    data.append(safe_excel_value(measurement.result_defect.category))

                                # Case 4: Generic → dump measurement value
                                else:
                                    raw_value = getattr(measurement, measurement.measurement_result_type.name, "")
                                    data.append(safe_excel_value(raw_value))

                            if skip:
                                break

                            sheet.append(data)

            # Wet Leakage Procedure
            elif "Wet Leakage" in procedure_def.name:
                sheet.title = "Wet Leakage"
                sheet.append([
                    "Serial Number", "TSD", "LEG", "final_result",
                    "Insulation Resistance", "Passed?", "Test Voltage",
                    "Leakage Current", "Current Trip Setpoint", "Water Temperature"
                ])

                for unit in units:
                    tests = ProcedureResult.objects.filter(
                        unit=unit,
                        procedure_definition_id=procedure_definition_id,
                        name=procedure_name
                    ).order_by("test_sequence_definition", "linear_execution_group")

                    for test in tests:
                        final_result_value = ProcedureResult_FinalResult.objects.filter(
                            procedure_result_id=test.id
                        ).values_list("final_result", flat=True).first() or "N/A"

                        for step_result in test.stepresult_set.all().exclude(archived=True):
                            data = [
                                safe_excel_value(unit.serial_number),
                                safe_excel_value(test.test_sequence_definition.name),
                                safe_excel_value(test.name),
                                safe_excel_value(final_result_value)
                            ]

                            for measurement in step_result.measurementresult_set.all().order_by("report_order"):
                                raw_value = getattr(measurement, measurement.measurement_result_type.name, "")
                                data.append(safe_excel_value(raw_value))

                            sheet.append(data)


                # EL Image Procedure
            elif "EL Image" in procedure_def.name:
                sheet.title = "EL Image"
                sheet.append([
                    "Serial Number", "TSD", "LEG", "final_result",
                    "Measurement Values"
                ])

                for unit in units:
                    tests = ProcedureResult.objects.filter(
                        unit=unit,
                        procedure_definition_id=procedure_definition_id,
                        name=procedure_name
                    ).order_by("test_sequence_definition", "linear_execution_group")

                    for test in tests:
                        final_result_value = ProcedureResult_FinalResult.objects.filter(
                            procedure_result_id=test.id
                        ).values_list("final_result", flat=True).first() or "N/A"

                        for step_result in test.stepresult_set.all().exclude(archived=True):
                            data = [
                                safe_excel_value(unit.serial_number),
                                safe_excel_value(test.test_sequence_definition.name),
                                safe_excel_value(test.name),
                                safe_excel_value(final_result_value)
                            ]

                            for measurement in step_result.measurementresult_set.all().order_by("report_order"):
                                if measurement.measurement_result_type.name == "result_files":
                                    if measurement.result_files.all().count():
                                        for azurefile in measurement.result_files.all():
                                            filetype = ""

                                            # Skip RAW files
                                            if "RAW" in azurefile.file.name:
                                                continue

                                            # Decide filetype
                                            if azurefile.file.name.lower().endswith(("xls", "xlsx", "txt", "csv")):
                                                filetype = "DataFiles"
                                            else:
                                                filetype = "ImageFiles"

                                            # Rename for Image files
                                            name = azurefile.file.name
                                            if filetype == "ImageFiles":
                                                temp = azurefile.file.name.split(".")
                                                base_name = temp[0]
                                                for sbstr in range(1, len(temp) - 1):
                                                    base_name = base_name + "." + temp[sbstr]

                                                name = "{}-{}-{}.{}".format(
                                                    base_name,
                                                    test.test_sequence_definition.name,
                                                    test.name,
                                                    temp[-1]
                                                )

                                            # Read file bytes
                                            bytes_io = BytesIO(azurefile.file.file.read())
                                            bytes_io.seek(0)

                                            # Try image adjustment if required
                                            try:
                                                temp_image = Image.open(bytes_io)
                                                if adjust_images:
                                                    width, height = temp_image.size
                                                    temp_image = temp_image.rotate(-90, expand=True)
                                                    temp_image = temp_image.resize((height, width))
                                                    temp_image = ImageOps.grayscale(temp_image)
                                                    temp_image = ImageOps.autocontrast(temp_image)

                                                image_bytes = BytesIO()
                                                temp_image.save(image_bytes, format="jpeg", quality=75)
                                                temp_image.close()
                                                content = image_bytes.getvalue()
                                                image_bytes.close()
                                            except Exception:
                                                bytes_io.seek(0)
                                                content = bytes_io.getvalue()

                                            bytes_io.close()

                                            # Write to ZIP
                                            zf.writestr(
                                                "{}/{}/{}/{}".format(
                                                    work_order.project.number,
                                                    work_order.name,
                                                    "EL Images",
                                                    name,
                                                ),
                                                content,
                                            )

                                else:
                                    raw_value = getattr(measurement, measurement.measurement_result_type.name, "")
                                    data.append(safe_excel_value(raw_value))

                            sheet.append(data)


            else:
                return Response(
                    {"error": f"Unsupported procedure type for {procedure_def.name}"},
                    status=400
                )

            # Save Excel into ZIP
            file_stream = BytesIO()
            excel_file.save(file_stream)
            file_stream.seek(0)
            zf.writestr(f"{work_order.name}_{procedure_def.name}.xlsx", file_stream.read())



        mem_zip.seek(0)
        response = HttpResponse(mem_zip.getvalue(), content_type="application/x-zip-compressed")
        response["Content-Disposition"] = f"attachment; filename={timezone.now().strftime('%b-%d-%Y-%H%M%S')}.zip"
        return response
