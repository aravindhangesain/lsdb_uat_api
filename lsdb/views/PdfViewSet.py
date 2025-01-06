import tempfile
from datetime import datetime
from rest_framework import viewsets
from lsdb.models import UnitType,ProcedureResult,ModuleProperty,MeasurementResult,Unit
import requests
from django.http import HttpResponse
from rest_framework.response import Response

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Spacer, Image, Paragraph
from rest_framework.viewsets import ViewSet


class PdfViewSet(viewsets.ViewSet):

    def list(self, request):
        work_order_id = request.query_params.get("work_order_id")
        procedure_definition_id = request.query_params.get("procedure_definition_id")
        
        if not work_order_id or not procedure_definition_id:
            return Response({"error": "Missing work_order_id or procedure_definition_id"}, status=400)
        
        
        procedure_results = ProcedureResult.objects.filter(
            work_order_id=work_order_id, procedure_definition_id=procedure_definition_id
        )

        rows = []  

        for procedure in procedure_results:
            unit = Unit.objects.filter(id=procedure.unit_id).first()
            if not unit:
                continue

            unittype = UnitType.objects.filter(id=unit.unit_type_id).first()
            if not unittype:
                continue

            moduleproperty = ModuleProperty.objects.filter(id=unittype.id).first()
            if not moduleproperty:
                continue

            
            measurements = MeasurementResult.objects.filter(step_result__procedure_result=procedure.id)
            result_dict = {measurement.name: measurement.result_double for measurement in measurements}

            
            rows.append({
                "test": procedure.name,
                "items": [
                    {
                        "model": unittype.model,
                        "serialNumber": unit.serial_number,
                        "Pmax": moduleproperty.nameplate_pmax,
                        "Voc": result_dict.get("Voc"),
                        "Vmp": result_dict.get("Vmp"),
                        "Isc": result_dict.get("Isc"),
                        "Imp": result_dict.get("Imp"),
                        "P": moduleproperty.nameplate_pmax,
                        "V": moduleproperty.voc,
                        "Vm": moduleproperty.vmp,
                        "Is": moduleproperty.isc,
                        "Im": moduleproperty.imp,
                    }
                ],
            })

        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        

        form_data = {
            "Title": "[Workbook Title]",
            "Customer": "[COMPANY NAME]",
            "Contact Name": "[Customer contact]",
            "Contact Email": "[Contact email]",
            "Project No.": "[PROJECT #]",
            "Revision": "Initial",
            "Status": "Initial",
            "Date": datetime.now().strftime("%d/%m/%Y"),
            "Classification": "Commercial in Confidence",
            "Author": "Hazem Ajlan",
            "Checked": "Hazem Ajlan",
            "Approved": "Jeff Cleland",
            "Provided By": "Kiwa PVEL (PVEL LLC)\n388 Devlin Road, Napa, CA 94558\nTel: +1 415 320 7835\nEnterprise No.: 27-0498579",
        }
        history_data = [
            ["Revision", "Date", "Summary"],
            ["", "", ""],
            ["", "", ""],
            ["", "", ""],
        ]

        rowImages = [
            {
                "serialNumber": "SN 20552349593549858",
                "items": [
                    {"Flash": "Post TC 200",
                     "imageUrl": "https://lumprodsta.blob.core.windows.net/prodcontainer/Images/3118c9fb-6014-4b93-8d4f-3aa6888604f1_165W_Poly_crystalline-panel_1%20%281%29.png"},
                    {"Flash": "Post TC 400",
                     "imageUrl": "https://lumprodsta.blob.core.windows.net/prodcontainer/Images/3118c9fb-6014-4b93-8d4f-3aa6888604f1_165W_Poly_crystalline-panel_1%20%281%29.png"},
                    {"Flash": "Post TC 600",
                     "imageUrl": "https://lumprodsta.blob.core.windows.net/prodcontainer/Images/3118c9fb-6014-4b93-8d4f-3aa6888604f1_165W_Poly_crystalline-panel_1%20%281%29.png"},
                    {"Flash": "Post TC 800",
                     "imageUrl": "https://lumprodsta.blob.core.windows.net/prodcontainer/Images/3118c9fb-6014-4b93-8d4f-3aa6888604f1_165W_Poly_crystalline-panel_1%20%281%29.png"},
                    {"Flash": "Post TC 800",
                     "imageUrl": "https://lumprodsta.blob.core.windows.net/prodcontainer/Images/3118c9fb-6014-4b93-8d4f-3aa6888604f1_165W_Poly_crystalline-panel_1%20%281%29.png"},
                    {"Flash": "Post TC 800",
                     "imageUrl": "https://lumprodsta.blob.core.windows.net/prodcontainer/Images/3118c9fb-6014-4b93-8d4f-3aa6888604f1_165W_Poly_crystalline-panel_1%20%281%29.png"},
                ],
            }
          
        ]

        try:
            doc = SimpleDocTemplate(
                temp_file.name,
                pagesize=letter,
                rightMargin=50,
                leftMargin=50,
                topMargin=10,
                bottomMargin=10,
            )

            elements = []

            styles = getSampleStyleSheet()
            title_style = styles["Heading1"]
            subtitle_style = styles["Heading2"]
            normal_style = styles["BodyText"]
            normal_style.fontSize = 6
            bold_style = styles["BodyText"]
            bold_style.fontName = "Helvetica-Bold"
            bold_style.fontSize = 6

            elements.append(Paragraph("9709 - BOM 2", title_style))
            elements.append(Paragraph(" TC600 , TC602, TC603, TC604 Flash Data", subtitle_style))
            elements.append(Paragraph("Hanwha Qcells", normal_style))

            elements.append(Spacer(1, 5))
            elements.append(Image("logo.PNG", width=400, height=150))
            elements.append(Spacer(1, 10))

            data = []
            for key, value in form_data.items():
                data.append([
                    Paragraph(f"<b>{key}</b>", bold_style),
                    Paragraph(value, normal_style),
                ])

            form_table = Table(data, colWidths=[100, 300])
            form_table.setStyle(
                TableStyle(
                    [
                        ("GRID", (0, 0), (-1, -1), 0.2, colors.black),
                        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                    ]
                )
            )
            elements.append(form_table)
            elements.append(Spacer(1, 10))

            history_title = Paragraph("History", subtitle_style)
            elements.append(history_title)

            history_table = Table(history_data, colWidths=[80, 80, 240])
            history_table.setStyle(
                TableStyle(
                    [
                        ("GRID", (0, 0), (-1, -1), 0.2, colors.black),
                        ("BACKGROUND", (0, 0), (-1, 0), colors.darkslateblue),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ]
                )
            )
            elements.append(history_table)
            elements.append(Spacer(1, 10))

            disclaimer_title = Paragraph(
                "IMPORTANT NOTICE AND DISCLAIMER", normal_style
            )
            disclaimer_text = Paragraph(
                "THE DATA ENCLOSED IS KIWA PVEL (PVEL LLC) CONFIDENTIAL INFORMATION. "
                "THIS DATA IS STRICTLY CONFIDENTIAL AND IS PROVIDED AS IS AND ON A NO RELIANCE BASIS. "
                "THIS DATA IS PROVIDED ONLY AS AN ACCOMMODATION TO THE CUSTOMER. "
                "AS OF THE DATE OF THIS DISCLOSURE THIS DATA IS NOT PART OF ANY KIWA PVEL DELIVERABLE. "
                "THE CUSTOMER IS INTENDED TO BE THE SOLE RECIPIENT OF THIS DISCLOSURE AND IS RESPONSIBLE "
                "FOR ITS USE, INTERPRETATION AND ANY FURTHER DISCLOSURE. KIWA PVEL DISCLAIMS ANY AND ALL "
                "LIABILITY ARISING FROM USE OR INTERPRETATION OF THIS DATA.",
                normal_style,
            )
            elements.append(disclaimer_title)
            elements.append(disclaimer_text)
            elements.append(Spacer(1, 10))

            classification_title = Paragraph("KEY TO DOCUMENT CLASSIFICATION", bold_style)
            elements.append(classification_title)

            classification_data = [
                ["Commercial in Confidence", "Not to be disclosed outside the Customer's organization"],
                [
                    "Customer's Discretion",
                    "Distribution for information only at the discretion of the Customer \n (subject to the above Important Notice and Disclaimer).",
                ],
            ]

            classification_table = Table(classification_data, colWidths=[180, 320])
            classification_table.setStyle(
                TableStyle(
                    [
                        ("GRID", (0, 0), (-1, -1), 0.2, colors.black),
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        ("FONTSIZE", (0, 0), (-1, 1), 8),

                    ]
                )
            )
            elements.append(classification_table)

            page_width = 550
            model_width = 120
            serial_number_width = 120
            remaining_width = page_width - (model_width + serial_number_width)
            other_column_width = remaining_width / 10

            col_widths = [model_width, serial_number_width] + [other_column_width] * 10

            for row in rows:
                test_name = row["test"]
                items = row["items"]

                header = [
                    [
                        f"{test_name}", "", f"Flash Data {test_name}", "", "", "", "",
                        "Percentage Different from Data Sheet",
                    ],
                    ["Model", "Serial Number", "Pmax", "Voc", "Vmp", "Isc", "Imp", "P", "V", "Vm", "Is", "Im"],
                ]

                data = header
                for item in items:
                    data.append([
                        item["model"],
                        item["serialNumber"],
                        item["Pmax"],
                        item["Voc"],
                        item["Vmp"],
                        item["Isc"],
                        item["Imp"],
                        item["P"],
                        item["V"],
                        item["Vm"],
                        item["Is"],
                        item["Im"],
                    ])

                table = Table(data, colWidths=col_widths)
                table.setStyle(
                    TableStyle(
                        [
                            ("BACKGROUND", (0, 0), (-1, 1), colors.darkslateblue),
                            ("TEXTCOLOR", (0, 0), (-1, 1), colors.whitesmoke),
                            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                            ("FONTNAME", (0, 0), (-1, 1), "Helvetica-Bold"),
                            ("FONTSIZE", (0, 0), (-1, 1), 8),
                            ("FONTSIZE", (0, 2), (-1, -1), 8),
                            ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
                            ("BOTTOMPADDING", (0, 2), (-1, -1), 8),
                            ("SPAN", (0, 0), (1, 0)),
                            ("SPAN", (2, 0), (6, 0)),
                            ("SPAN", (7, 0), (11, 0)),
                            ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
                        ]
                    )
                )
                elements.append(table)
                elements.append(Spacer(1, 20))

            temp_dir = tempfile.mkdtemp()

            def download_image(url, filename):
                """Download an image from a URL."""
                response = requests.get(url)
                if response.status_code == 200:
                    with open(filename, "wb") as f:
                        f.write(response.content)
                    return filename
                return None

            styles = getSampleStyleSheet()
            text_style = styles["BodyText"]

            import os

            for row in rowImages:
                serial_number_table = Table(
                    [[Paragraph(f"Serial Number: {row['serialNumber']}")]],
                    colWidths=[500],
                )
                serial_number_table.setStyle(
                    TableStyle(
                        [
                            ("BACKGROUND", (0, 0), (-1, -1), colors.darkslateblue),
                            ("TEXTCOLOR", (0, 0), (-1, -1), colors.white),
                            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                            ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
                            ("FONTSIZE", (0, 0), (-1, -1), 12),
                            ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
                            ("LEFTPADDING", (0, 0), (-1, -1), 10),
                            ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                            ("TOPPADDING", (0, 0), (-1, -1), 5),
                            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                        ]
                    )
                )
                elements.append(serial_number_table)

                image_grid = []

                for item in row["items"]:
                    local_image_path = os.path.join(temp_dir, f"image_{item['Flash']}.png")
                    downloaded_image = download_image(item["imageUrl"], local_image_path)

                    if downloaded_image:
                        flash_text = Paragraph(item["Flash"], text_style)
                        img = Image(downloaded_image, width=200, height=150)
                        image_grid.append([flash_text, img])

                num_columns = len(row["items"])
                total_width = 500
                column_width = total_width / num_columns

                grid_table = Table([list(row) for row in zip(*image_grid)], colWidths=[column_width] * num_columns)
                grid_table.setStyle(
                    TableStyle(
                        [
                            ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
                            ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                            ("VALIGN", (0, 0), (-1, -1), "TOP"),
                            ("LEFTPADDING", (0, 0), (-1, -1), 10),
                            ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                            ("TOPPADDING", (0, 0), (-1, -1), 5),
                            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                        ]
                    )
                )
                elements.append(grid_table)

            doc.build(elements)

            with open(temp_file.name, "rb") as pdf_file:
                response = HttpResponse(pdf_file.read(), content_type="application/pdf")
                response["Content-Disposition"] = f"attachment; filename=flash_data_{datetime.now()}.pdf"
                return response

        finally:
            temp_file.close()
            if temp_file.name:
                import os
                os.remove(temp_file.name)
