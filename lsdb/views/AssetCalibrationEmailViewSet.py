from calendar import monthrange
from django.conf import settings
from rest_framework import viewsets
from datetime import date, timedelta
from lsdb.models import AssetCalibration
from rest_framework.response import Response
from rest_framework.decorators import action
from django.core.mail import EmailMultiAlternatives
from lsdb.serializers import AssetCalibrationSerializer



class AssetCalibrationEmailViewSet(viewsets.ModelViewSet):
    queryset = AssetCalibration.objects.all()
    serializer_class = AssetCalibrationSerializer

    @action(detail=False, methods=['get'])
    def asset_list(self, request):
        result, error = self.get_filtered_assets(request)
        if error:
            return Response(error, status=400)
        return Response({"data": result})
    
    @action(detail=False, methods=['get','post'])
    def send_email(self, request):
        result, error = self.get_filtered_assets(request)
        if error:
            return Response(error, status=400)
        if not result:
            return Response({"message": "No data to send"}, status=200)
        table_rows = ""
        for item in result:
            table_rows += f"""
            <tr>
                <td>{item['asset_id']}</td>
                <td>{item['asset_name']}</td>
                <td>{item['asset_type']}</td>
                <td>{item['last_calibrated_date']}</td>
                <td>{item['schedule_for_calibration']}</td>
                <td>{item['calibration_due_date']}</td>
            </tr>
            """
        html_content = f"""
        <html>
            <body>
                <p>Dear Team,</p>
                <p>Below are the assets due for calibration:</p>              
                <p>Please take action.</p>
                <table border="1" cellpadding="6" cellspacing="0">
                    <thead>
                        <tr>
                            <th>Asset ID</th>
                            <th>Asset Name</th>
                            <th>Asset Type</th>
                            <th>Last Calibrated</th>
                            <th>Schedule</th>
                            <th>Calibration Due Date</th>
                        </tr>
                    </thead>
                    <tbody>
                        {table_rows}
                    </tbody>
                </table>
                <p>Regards,<br/>Asset Management System</p>
            </body>
        </html>
        """
        email = EmailMultiAlternatives(
            subject="Calibration Due Assets",
            body="Please view in HTML format",
            from_email=settings.EMAIL_HOST_USER,
            to=["manikandanr@gesain.com", request.user.email],
        )
        email.attach_alternative(html_content, "text/html")
        email.send(fail_silently=False)
        return Response({"message": "Email sent successfully"})
    
    def get_filtered_assets(self, request):
        try:
            date_input = request.query_params.get('date')
            all_flag = request.query_params.get('all')
            all_flag = str(all_flag).lower() == "true"
            if all_flag and date_input:
                return None, {"error": "Do not pass date when all=true"}
            if not all_flag and not date_input:
                return None, {"error": "date is required when all=false"}
            ranges = []
            if all_flag:
                today = date.today()
                curr_start = date(today.year, today.month, 1)
                curr_end = date(today.year, today.month, monthrange(today.year, today.month)[1])
                prev_month = today.month - 1 or 12
                prev_year = today.year if today.month != 1 else today.year - 1
                prev_start = date(prev_year, prev_month, 1)
                prev_end = date(prev_year, prev_month, monthrange(prev_year, prev_month)[1])
                ranges.extend([(prev_start, prev_end), (curr_start, curr_end)])
            else:
                try:
                    year, month = map(int, date_input.split('-'))
                except:
                    return None, {"error": "Invalid date format. Use YYYY-MM"}
                start_date = date(year, month, 1)
                end_date = date(year, month, monthrange(year, month)[1])
                ranges.append((start_date, end_date))
            queryset = AssetCalibration.objects.all()
            result = []
            for obj in queryset:
                if obj.last_calibrated_date and obj.schedule_for_calibration:
                    next_date = (
                        obj.last_calibrated_date + timedelta(days=obj.schedule_for_calibration)
                    ).date()
                    for start_date, end_date in ranges:
                        if start_date <= next_date <= end_date:
                            result.append({
                                "asset_id": obj.asset_number,
                                "asset_name": obj.asset_name,
                                "asset_type": obj.asset_type.name if obj.asset_type else None,
                                "last_calibrated_date": obj.last_calibrated_date.date(),
                                "schedule_for_calibration": obj.schedule_for_calibration,
                                "calibration_due_date": next_date
                            })
                            break

            result.sort(key=lambda x: x['calibration_due_date'])
            return result, None
        except Exception as e:
            return None, {"error": str(e)}