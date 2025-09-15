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
from django.db.models import F, Value
from django.db.models.functions import Replace, Lower

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
            ).values(
                'procedure_definition__id',
                'procedure_definition__name',
                'name'
            ).exclude(group_id=45)
            procedures_dict = {}
            for proc in procedures:
                pid = proc['procedure_definition__id']
                pname = proc.get('name')
                if pid not in procedures_dict:
                    procedures_dict[pid] = {
                        "procedure_definition_id": pid,
                        "procedure_definition_name": proc['procedure_definition__name'],
                        "procedure_names": []
                    }
                if pname and pname not in procedures_dict[pid]["procedure_names"]:
                    procedures_dict[pid]["procedure_names"].append(pname)
            workorder_data = {
                "workorder_id": workorder.id,
                "workorder_name": workorder.name,
                "procedure_definitions": list(procedures_dict.values())
            }
            data["workorders"].append(workorder_data)
        return Response(data)
    

    # @action(detail=True, methods=['get'], url_path='download')   
    # def download(self, request, number=None):
    #     """
    #     Endpoint: /api/1.0/projectdownload/<pk>/download/
    #     Query Params: workorder_id, procedure_definition_id, procedure_name
    #     Supports multiple comma-separated values.
    #     Example:
    #     ?workorder_id=1,2&procedure_definition_id=2,3&procedure_name=Pre-Light Soak,Pre-Stress
    #     """

    #     # ----------------------------
    #     # Helpers
    #     # ----------------------------
    #     def normalize_name(queryset):
    #         """Annotates queryset with normalized_name (lowercase, no spaces/dashes)."""
    #         return queryset.annotate(
    #             normalized_name=Lower(
    #                 Replace(
    #                     Replace(F("name"), Value("-"), Value("")),
    #                     Value(" "), Value("")
    #                 )
    #             )
    #         )

    #     def normalize_value(val: str) -> str:
    #         """Normalize input string (lowercase, no spaces/dashes)."""
    #         return val.replace("-", "").replace(" ", "").lower()

    #     def safe_excel_value(val):
    #         """Convert any object to safe Excel cell value."""
    #         if hasattr(val, "all"):  # ManyToMany manager
    #             return ", ".join(str(v) for v in val.all())
    #         if isinstance(val, (str, int, float, type(None))):
    #             return val
    #         return str(val)

    #     # ----------------------------
    #     # Validate query params
    #     # ----------------------------
    #     workorder_ids = request.GET.get("workorder_id")
    #     procedure_definition_ids = request.GET.get("procedure_definition_id")
    #     procedure_names = request.GET.get("procedure_name")
    #     adjust_images = False  # Toggle for EL image adjustment

    #     if not workorder_ids:
    #         return Response({"error": "workorder_id is required"}, status=400)

    #     # Convert CSV params → lists
    #     workorder_ids = [wid.strip() for wid in workorder_ids.split(",") if wid.strip()]
    #     procedure_definition_ids = (
    #         [pid.strip() for pid in procedure_definition_ids.split(",") if pid.strip()]
    #         if procedure_definition_ids else []
    #     )
    #     procedure_names = (
    #         [pn.strip() for pn in procedure_names.split(",") if pn.strip()]
    #         if procedure_names else []
    #     )

    #     project = get_object_or_404(Project, number=number)

    #     mem_zip = BytesIO()
    #     with zipfile.ZipFile(mem_zip, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:

    #         # ---- loop over all workorders
    #         for workorder_id in workorder_ids:
    #             work_order = get_object_or_404(project.workorder_set, id=workorder_id)

    #             if not procedure_definition_ids:
    #                 proc_defs = ProcedureDefinition.objects.all()
    #             else:
    #                 proc_defs = ProcedureDefinition.objects.filter(id__in=procedure_definition_ids)

    #             # ---- loop over all procedure definitions
    #             for procedure_def in proc_defs:

    #                 if not procedure_names:
    #                     proc_names = (
    #                         ProcedureResult.objects.filter(
    #                             work_order=work_order,
    #                             procedure_definition=procedure_def
    #                         ).values_list("name", flat=True).exclude(group_id=45).distinct()
    #                     )
    #                 else:
    #                     proc_names = procedure_names

    #                 # ---- loop over all procedure names
    #                 for procedure_name in proc_names:
    #                     normalized_proc_name = normalize_value(procedure_name)

    #                     # Create workbook
    #                     excel_file = Workbook()
    #                     sheet = excel_file.active

    #                     # Fetch units linked to this work order
    #                     units = Unit.objects.filter(
    #                         procedureresult__work_order=work_order
    #                     ).distinct()

    #                     # ---------------------------
    #                     # I-V Flash Procedure
    #                     # ---------------------------
    #                     if "I-V" in procedure_def.name:
    #                         sheet.title = "Flash"
    #                         sheet.append([
    #                             "Serial Number", "TSD", "LEG", "final_result",
    #                             "Pmp", "Voc", "Vmp", "Isc", "Imp", "Irradiance", "Temperature"
    #                         ])

    #                         for unit in units:
    #                             tests = normalize_name(
    #                                 ProcedureResult.objects.filter(
    #                                     unit=unit,
    #                                     procedure_definition_id=procedure_def.id,
    #                                 )
    #                             ).filter(
    #                                 normalized_name=normalized_proc_name
    #                             ).order_by("test_sequence_definition", "linear_execution_group")

    #                             for test in tests:
    #                                 final_result_value = ProcedureResult_FinalResult.objects.filter(
    #                                     procedure_result_id=test.id
    #                                 ).values_list("final_result", flat=True).first() or "N/A"

    #                                 for step_result in test.stepresult_set.all().exclude(archived=True):
    #                                     data = [
    #                                         safe_excel_value(unit.serial_number),
    #                                         safe_excel_value(test.test_sequence_definition.name),
    #                                         safe_excel_value(test.name),
    #                                         safe_excel_value(final_result_value)
    #                                     ]

    #                                     for measurement in step_result.measurementresult_set.all().order_by("report_order"):

    #                                         if measurement.measurement_result_type.name == "result_files":
    #                                             if measurement.result_files.all().count():
    #                                                 for azurefile in measurement.result_files.all():
    #                                                     path = "Flash Data/"
    #                                                     if "200" in step_result.name:
    #                                                         path += "200W/"
    #                                                     elif "Rear" in test.procedure_definition.name:
    #                                                         path += "Rear/"
    #                                                     path += "FLASH/{}/{}".format(
    #                                                         test.test_sequence_definition.name,
    #                                                         test.name
    #                                                     )
    #                                                     file_bytes = azurefile.file.file.read()
    #                                                     zf.writestr(
    #                                                         "{}/{}/{}/{}/{}".format(
    #                                                             work_order.project.number,
    #                                                             work_order.name,
    #                                                             "Flash Data",
    #                                                             path,
    #                                                             azurefile.file.name,
    #                                                         ),
    #                                                         file_bytes
    #                                                     )

    #                                         elif measurement.measurement_result_type.name == "result_datetime":
    #                                             continue

    #                                         else:
    #                                             raw_value = getattr(
    #                                                 measurement,
    #                                                 measurement.measurement_result_type.name,
    #                                                 "",
    #                                             )
    #                                             data.append(safe_excel_value(raw_value))

    #                                     sheet.append(data)

    #                     # ---------------------------
    #                     # Visual Inspection
    #                     # ---------------------------
    #                     elif "Visual Inspection" in procedure_def.name:
    #                         sheet.title = "Visual Inspection"
    #                         sheet.append([
    #                             "Serial Number", "TSD", "LEG", "final_result",
    #                             "Defect", "Category", "Notes", "Images"
    #                         ])

    #                         for unit in units:
    #                             tests = normalize_name(
    #                                 ProcedureResult.objects.filter(
    #                                     unit=unit,
    #                                     procedure_definition_id=procedure_def.id,
    #                                 )
    #                             ).filter(
    #                                 normalized_name=normalized_proc_name
    #                             ).order_by("test_sequence_definition", "linear_execution_group")

    #                             for test in tests:
    #                                 final_result_value = ProcedureResult_FinalResult.objects.filter(
    #                                     procedure_result_id=test.id
    #                                 ).values_list("final_result", flat=True).first() or "N/A"

    #                                 skip = False
    #                                 for step_result in test.stepresult_set.all().exclude(archived=True):
    #                                     data = [
    #                                         unit.serial_number,
    #                                         safe_excel_value(test.test_sequence_definition.name),
    #                                         safe_excel_value(test.name),
    #                                         safe_excel_value(final_result_value)
    #                                     ]

    #                                     for measurement in step_result.measurementresult_set.all().order_by("report_order"):

    #                                         if step_result.name == "Inspect Module":
    #                                             if getattr(measurement, measurement.measurement_result_type.name):
    #                                                 skip = True
    #                                                 data.append("No Defects Observed")
    #                                                 sheet.append(data)

    #                                         elif skip:
    #                                             break

    #                                         elif measurement.measurement_result_type.name == "result_files":
    #                                             if measurement.result_files.all().count():
    #                                                 for azurefile in measurement.result_files.all():
    #                                                     file_bytes = azurefile.file.file.read()
    #                                                     zf.writestr(
    #                                                         "{}/{}/{}/{}".format(
    #                                                             work_order.project.number,
    #                                                             work_order.name,
    #                                                             "VI Images",
    #                                                             azurefile.file.name,
    #                                                         ),
    #                                                         file_bytes
    #                                                     )
    #                                                     data.append(azurefile.file.name)

    #                                         elif measurement.result_defect is not None and measurement.measurement_result_type.name == "result_defect":
    #                                             data.append(safe_excel_value(measurement.result_defect.short_name))
    #                                             data.append(safe_excel_value(measurement.result_defect.category))

    #                                         else:
    #                                             raw_value = getattr(
    #                                                 measurement,
    #                                                 measurement.measurement_result_type.name,
    #                                                 "",
    #                                             )
    #                                             data.append(safe_excel_value(raw_value))

    #                                     if skip:
    #                                         break
    #                                     sheet.append(data)

    #                     # ---------------------------
    #                     # Wet Leakage
    #                     # ---------------------------
    #                     elif "Wet Leakage" in procedure_def.name:
    #                         sheet.title = "Wet Leakage"
    #                         sheet.append([
    #                             "Serial Number", "TSD", "LEG", "final_result",
    #                             "Insulation Resistance", "Passed?", "Test Voltage",
    #                             "Leakage Current", "Current Trip Setpoint", "Water Temperature"
    #                         ])

    #                         for unit in units:
    #                             tests = normalize_name(
    #                                 ProcedureResult.objects.filter(
    #                                     unit=unit,
    #                                     procedure_definition_id=procedure_def.id,
    #                                 )
    #                             ).filter(
    #                                 normalized_name=normalized_proc_name
    #                             ).order_by("test_sequence_definition", "linear_execution_group")

    #                             for test in tests:
    #                                 final_result_value = ProcedureResult_FinalResult.objects.filter(
    #                                     procedure_result_id=test.id
    #                                 ).values_list("final_result", flat=True).first() or "N/A"

    #                                 for step_result in test.stepresult_set.all().exclude(archived=True):
    #                                     data = [
    #                                         safe_excel_value(unit.serial_number),
    #                                         safe_excel_value(test.test_sequence_definition.name),
    #                                         safe_excel_value(test.name),
    #                                         safe_excel_value(final_result_value)
    #                                     ]

    #                                     for measurement in step_result.measurementresult_set.all().order_by("report_order"):
    #                                         raw_value = getattr(
    #                                             measurement,
    #                                             measurement.measurement_result_type.name,
    #                                             "",
    #                                         )
    #                                         data.append(safe_excel_value(raw_value))

    #                                     sheet.append(data)

    #                     # ---------------------------
    #                     # EL Image
    #                     # ---------------------------
    #                     elif "EL Image" in procedure_def.name:
    #                         sheet.title = "EL Image"
    #                         sheet.append([
    #                             "Serial Number", "TSD", "LEG", "final_result",
    #                             "Measurement Values"
    #                         ])

    #                         for unit in units:
    #                             tests = normalize_name(
    #                                 ProcedureResult.objects.filter(
    #                                     unit=unit,
    #                                     procedure_definition_id=procedure_def.id,
    #                                 )
    #                             ).filter(
    #                                 normalized_name=normalized_proc_name
    #                             ).order_by("test_sequence_definition", "linear_execution_group")

    #                             for test in tests:
    #                                 final_result_value = ProcedureResult_FinalResult.objects.filter(
    #                                     procedure_result_id=test.id
    #                                 ).values_list("final_result", flat=True).first() or "N/A"

    #                                 for step_result in test.stepresult_set.all().exclude(archived=True):
    #                                     data = [
    #                                         safe_excel_value(unit.serial_number),
    #                                         safe_excel_value(test.test_sequence_definition.name),
    #                                         safe_excel_value(test.name),
    #                                         safe_excel_value(final_result_value)
    #                                     ]

    #                                     for measurement in step_result.measurementresult_set.all().order_by("report_order"):
    #                                         if measurement.measurement_result_type.name == "result_files":
    #                                             if measurement.result_files.all().count():
    #                                                 for azurefile in measurement.result_files.all():
    #                                                     if "RAW" in azurefile.file.name:
    #                                                         continue

    #                                                     filetype = "DataFiles" if azurefile.file.name.lower().endswith(("xls", "xlsx", "txt", "csv")) else "ImageFiles"

    #                                                     name = azurefile.file.name
    #                                                     if filetype == "ImageFiles":
    #                                                         temp = azurefile.file.name.split(".")
    #                                                         base_name = ".".join(temp[:-1])
    #                                                         name = "{}-{}-{}.{}".format(
    #                                                             base_name,
    #                                                             test.test_sequence_definition.name,
    #                                                             test.name,
    #                                                             temp[-1]
    #                                                         )

    #                                                     bytes_io = BytesIO(azurefile.file.file.read())
    #                                                     bytes_io.seek(0)

    #                                                     try:
    #                                                         temp_image = Image.open(bytes_io)
    #                                                         if adjust_images:
    #                                                             width, height = temp_image.size
    #                                                             temp_image = temp_image.rotate(-90, expand=True)
    #                                                             temp_image = temp_image.resize((height, width))
    #                                                             temp_image = ImageOps.grayscale(temp_image)
    #                                                             temp_image = ImageOps.autocontrast(temp_image)

    #                                                         image_bytes = BytesIO()
    #                                                         temp_image.save(image_bytes, format="jpeg", quality=75)
    #                                                         temp_image.close()
    #                                                         content = image_bytes.getvalue()
    #                                                         image_bytes.close()
    #                                                     except Exception:
    #                                                         bytes_io.seek(0)
    #                                                         content = bytes_io.getvalue()
    #                                                     bytes_io.close()

    #                                                     zf.writestr(
    #                                                         "{}/{}/{}/{}".format(
    #                                                             work_order.project.number,
    #                                                             work_order.name,
    #                                                             "EL Images",
    #                                                             name,
    #                                                         ),
    #                                                         content,
    #                                                     )
    #                                         else:
    #                                             raw_value = getattr(
    #                                                 measurement,
    #                                                 measurement.measurement_result_type.name,
    #                                                 "",
    #                                             )
    #                                             data.append(safe_excel_value(raw_value))

    #                                     sheet.append(data)

    #                     else:
    #                         return Response(
    #                             {"error": f"Unsupported procedure type for {procedure_def.name}"},
    #                             status=400
    #                         )

    #                     # Save Excel into ZIP
    #                     file_stream = BytesIO()
    #                     excel_file.save(file_stream)
    #                     file_stream.seek(0)
    #                     zf.writestr(
    #                         f"{work_order.name}_{procedure_def.name}_{procedure_name}.xlsx",
    #                         file_stream.read(),
    #                     )

    #     mem_zip.seek(0)
    #     response = HttpResponse(mem_zip.getvalue(), content_type="application/x-zip-compressed")
    #     response["Content-Disposition"] = f"attachment; filename={timezone.now().strftime('%b-%d-%Y-%H%M%S')}.zip"
    #     return response



    @action(detail=True, methods=['post'], url_path='download')
    def download(self, request, number=None):
        """
        Endpoint: POST /api/1.0/projectdownload/<pk>/download/

        Example Body JSON:
        {
        "workorder_id": [1],
        "procedures": [
            {
            "procedure_definition_id": 2,
            "procedure_names": ["Pre-Stress","Post-Stress"]
            },
            {
            "procedure_definition_id": 3,
            "procedure_names": ["Pre Light Soak","Post Light Soak"]
            }
        ]
        }
        """

        # ----------------------------
        # Helpers
        # ----------------------------
        def normalize_name(queryset):
            return queryset.annotate(
                normalized_name=Lower(
                    Replace(
                        Replace(F("name"), Value("-"), Value("")),
                        Value(" "), Value("")
                    )
                )
            )

        def normalize_value(val: str) -> str:
            return val.replace("-", "").replace(" ", "").lower()

        def safe_excel_value(val):
            if hasattr(val, "all"):
                return ", ".join(str(v) for v in val.all())
            if isinstance(val, (str, int, float, type(None))):
                return val
            return str(val)

        # ----------------------------
        # Validate body payload
        # ----------------------------
        workorder_id = request.data.get("workorder_id")
        procedures = request.data.get("procedures", [])
        adjust_images = False

        if not workorder_id:
            return Response({"error": "workorder id are required"}, status=400)

        project = get_object_or_404(Project, number=number)

        work_order = get_object_or_404(project.workorder_set, id=workorder_id)
        if not procedures:
            procedures = []
            procedure_results = ProcedureResult.objects.filter(work_order=work_order).exclude(group_id=45)
            proc_defs = procedure_results.values_list("procedure_definition_id", flat=True).distinct()

            for proc_def_id in proc_defs:
                proc_names = (
                    procedure_results.filter(procedure_definition_id=proc_def_id)
                    .values_list("name", flat=True)
                    .distinct()
                )
                procedures.append({
                    "procedure_definition_id": proc_def_id,
                    "procedure_names": list(proc_names)
                })

        files_to_return = []     
        extra_files_exist = False

        mem_zip = BytesIO()
        with zipfile.ZipFile(mem_zip, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
                # ---- loop over each procedure_definition group
                for proc in procedures:
                    procedure_def_id = proc.get("procedure_definition_id")
                    procedure_names = proc.get("procedure_names", [])

                    procedure_def = get_object_or_404(ProcedureDefinition, id=procedure_def_id)

                    # fallback if no names given → get all names from DB
                    if not procedure_names:
                        procedure_names = ProcedureResult.objects.filter(
                            work_order=work_order,
                            procedure_definition=procedure_def
                        ).values_list("name", flat=True).exclude(group_id=45).distinct()

                    # ---- loop over all procedure names under this definition
                    for procedure_name in procedure_names:
                        normalized_proc_name = normalize_value(procedure_name)

                        # create Excel workbook
                        excel_file = Workbook()
                        sheet = excel_file.active

                        units = Unit.objects.filter(
                            procedureresult__work_order=work_order
                        ).distinct()

                        # ========================================================
                        #   I-V Flash Procedure
                        # ========================================================
                        if "I-V" in procedure_def.name:
                            sheet.title = "Flash"
                            sheet.append([
                                "Serial Number", "TSD", "LEG", "final_result",
                                "Pmp", "Voc", "Vmp", "Isc", "Imp", "Irradiance", "Temperature"
                            ])
                            for unit in units:
                                tests = normalize_name(
                                    ProcedureResult.objects.filter(
                                        unit=unit,
                                        procedure_definition_id=procedure_def.id,
                                    )
                                ).filter(
                                    normalized_name=normalized_proc_name
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
                                            elif measurement.measurement_result_type.name == "result_datetime":
                                                continue
                                            else:
                                                raw_value = getattr(
                                                    measurement,
                                                    measurement.measurement_result_type.name,
                                                    "",
                                                )
                                                data.append(safe_excel_value(raw_value))
                                        sheet.append(data)

                        # ========================================================
                        # Visual Inspection
                        # ========================================================
                        elif "Visual Inspection" in procedure_def.name:
                            sheet.title = "Visual Inspection"
                            sheet.append([
                                "Serial Number", "TSD", "LEG", "final_result",
                                "Defect", "Category", "Notes", "Images"
                            ])

                            for unit in units:
                                tests = normalize_name(
                                    ProcedureResult.objects.filter(
                                        unit=unit,
                                        procedure_definition_id=procedure_def.id,
                                    )
                                ).filter(
                                    normalized_name=normalized_proc_name
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

                                            if step_result.name == "Inspect Module":
                                                if getattr(measurement, measurement.measurement_result_type.name):
                                                    skip = True
                                                    data.append("No Defects Observed")
                                                    sheet.append(data)

                                            elif skip:
                                                break

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

                                            elif measurement.result_defect is not None and measurement.measurement_result_type.name == "result_defect":
                                                data.append(safe_excel_value(measurement.result_defect.short_name))
                                                data.append(safe_excel_value(measurement.result_defect.category))

                                            else:
                                                raw_value = getattr(
                                                    measurement,
                                                    measurement.measurement_result_type.name,
                                                    "",
                                                )
                                                data.append(safe_excel_value(raw_value))

                                        if skip:
                                            break
                                        sheet.append(data)

                        # ========================================================
                        # Wet Leakage
                        # ========================================================
                        elif "Wet Leakage" in procedure_def.name:
                            sheet.title = "Wet Leakage"
                            sheet.append([
                                "Serial Number", "TSD", "LEG", "final_result",
                                "Insulation Resistance", "Passed?", "Test Voltage",
                                "Leakage Current", "Current Trip Setpoint", "Water Temperature"
                            ])

                            for unit in units:
                                tests = normalize_name(
                                    ProcedureResult.objects.filter(
                                        unit=unit,
                                        procedure_definition_id=procedure_def.id,
                                    )
                                ).filter(
                                    normalized_name=normalized_proc_name
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
                                            raw_value = getattr(
                                                measurement,
                                                measurement.measurement_result_type.name,
                                                "",
                                            )
                                            data.append(safe_excel_value(raw_value))

                                        sheet.append(data)

                        # ========================================================
                        # EL Image
                        # ========================================================
                        elif "EL Image" in procedure_def.name:
                            sheet.title = "EL Image"
                            sheet.append([
                                "Serial Number", "TSD", "LEG", "final_result",
                                "Measurement Values"
                            ])

                            for unit in units:
                                tests = normalize_name(
                                    ProcedureResult.objects.filter(
                                        unit=unit,
                                        procedure_definition_id=procedure_def.id,
                                    )
                                ).filter(
                                    normalized_name=normalized_proc_name
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
                                                        if "RAW" in azurefile.file.name:
                                                            continue

                                                        filetype = "DataFiles" if azurefile.file.name.lower().endswith(("xls", "xlsx", "txt", "csv")) else "ImageFiles"

                                                        name = azurefile.file.name
                                                        if filetype == "ImageFiles":
                                                            temp = azurefile.file.name.split(".")
                                                            base_name = ".".join(temp[:-1])
                                                            name = "{}-{}-{}.{}".format(
                                                                base_name,
                                                                test.test_sequence_definition.name,
                                                                test.name,
                                                                temp[-1]
                                                            )

                                                        bytes_io = BytesIO(azurefile.file.file.read())
                                                        bytes_io.seek(0)

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
                                                raw_value = getattr(
                                                    measurement,
                                                    measurement.measurement_result_type.name,
                                                    "",
                                                )
                                                data.append(safe_excel_value(raw_value))
                                        sheet.append(data)

                        else:
                            return Response(
                                {"error": f"Unsupported procedure type for {procedure_def.name}"},
                                status=400
                            )
                        file_stream = BytesIO()
                        excel_file.save(file_stream)
                        file_stream.seek(0)
                        files_to_return.append({
                            "name": f"{work_order.name}_{procedure_def.name}_{procedure_name}.xlsx",
                            "content": file_stream.getvalue(),
                            "force_zip": False
                        })
                        file_stream.close()

        if len(files_to_return) == 1 and not extra_files_exist:
            file = files_to_return[0]
            response = HttpResponse(
                file["content"],
                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            response["Content-Disposition"] = f'attachment; filename="{file["name"]}"'
            return response

        mem_zip = BytesIO()
        with zipfile.ZipFile(mem_zip, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
            for file in files_to_return:
                zf.writestr(file["name"], file["content"])
        mem_zip.seek(0)
        response = HttpResponse(mem_zip.getvalue(), content_type="application/x-zip-compressed")
        response["Content-Disposition"] = (f'attachment; filename="{work_order.project.number}-{timezone.now().strftime("%b-%d-%Y-%H%M%S")}.zip"')
        return response
