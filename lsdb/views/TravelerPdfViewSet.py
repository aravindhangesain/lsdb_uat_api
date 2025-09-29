from rest_framework import viewsets
from django.http import HttpResponse
from rest_framework.decorators import action
from django.db import transaction
import tempfile
from datetime import datetime
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from lsdb.models import Unit
from lsdb.serializers import UnitGroupedTravelerSerializer

class TravelerPdfViewSet(viewsets.ModelViewSet):
    serializer_class = UnitGroupedTravelerSerializer
    queryset = Unit.objects.all()

    @transaction.atomic
    @action(detail=False, methods=['get'], url_path='grouped-history-pdf')
    def grouped_history_pdf(self, request):
        serial_number = request.query_params.get("serial_number")
        if not serial_number:
            return HttpResponse("Serial number parameter is required.", status=400)
        unit = Unit.objects.filter(serial_number=serial_number).first()
        if not unit:
            return HttpResponse("Invalid serial number.", status=404)
        
        serializer = self.serializer_class(unit, many=False, context={'request': request})
        unit_type = serializer.data.pop('unit_type')
        sequences_results = serializer.data.pop('sequences_results')
        module_property = unit_type.pop('module_property')

        def safe_paragraph(value, style):
            if value is None:
                value = ""
            return Paragraph(str(value), style)
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        try:
            doc = SimpleDocTemplate(temp_file.name, pagesize=letter)
            styles = getSampleStyleSheet()
            elements = []
            title_style = ParagraphStyle(
                name="TitleCentered",
                parent=styles["Heading1"],
                alignment=TA_CENTER
            )
            elements.append(Paragraph(f"Traveler History for {serial_number}", title_style))
            elements.append(Spacer(1, 12))
            header_data = [
                ["Project Number", serializer.data.pop("project_number")],
                ["Project Manager", serializer.data.pop("project_manager")],
                ["Customer", serializer.data.pop("customer_name")],
                ["Work Order", serializer.data.pop("work_order_name")],
                ["Serial Number", serial_number],
            ]
            header_table = Table(header_data, colWidths=[150, 300])
            header_table.setStyle(TableStyle([
                ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ]))
            elements.append(header_table)
            elements.append(Spacer(1, 12))
            centered_heading = ParagraphStyle(
                name="CenteredHeading",
                parent=styles["Heading2"],
                alignment=TA_CENTER,
                spaceAfter=12
            )
            wrap_style = ParagraphStyle(name="wrap", fontSize=8, leading=10)
            for seq in sequences_results:
                seq_name = f"Sequence {seq.get('linear_execution_group')}: {seq.get('name')}"
                elements.append(Paragraph(seq_name, centered_heading))
                proc_table_data = [["Procedure", "Operator", "Test_Date", "Disposition", "Reviewer", "Reviewer_Date"]]
                for result in seq.get('procedure_results', []):
                    proc_table_data.append([
                        safe_paragraph(result.get('procedure_definition_name'), wrap_style),
                        safe_paragraph(result.get('username'), wrap_style),
                        safe_paragraph(result.get('completion_date'), wrap_style),
                        safe_paragraph(result.get('disposition_name'), wrap_style),
                        safe_paragraph(result.get('reviewed_by_user'), wrap_style),
                        safe_paragraph(result.get('review_datetime'), wrap_style),
                    ])
                usable_width = letter[0] - 1.5 * inch
                base_widths = [140, 140, 120, 80, 160, 140]
                scale = usable_width / sum(base_widths)
                col_widths = [w * scale for w in base_widths]
                proc_table = Table(proc_table_data, colWidths=col_widths)
                proc_table.setStyle(TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#DCE6F2")), 
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("ALIGN", (0, 0), (-1, 0), "CENTER"),    
                    ("ALIGN", (0, 1), (0, -1), "LEFT"),      
                    ("ALIGN", (1, 1), (-2, -1), "CENTER"),    
                    ("ALIGN", (4, 1), (4, -1), "LEFT"),      
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                    ("LEFTPADDING", (0,0), (-1,-1), 2),
                    ("RIGHTPADDING", (0,0), (-1,-1), 2),
                ]))
                elements.append(proc_table)
                elements.append(Spacer(1, 12))
            doc.build(elements)
            with open(temp_file.name, "rb") as pdf_file:
                response = HttpResponse(pdf_file.read(), content_type="application/pdf")
                response["Content-Disposition"] = (
                    f"attachment; filename=Traveler_History_{datetime.now().strftime('%Y-%m-%d')}.pdf"
                )
                return response
        finally:
            temp_file.close()
            import os
            if temp_file.name:
                os.remove(temp_file.name)
