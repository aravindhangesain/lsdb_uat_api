import calendar
from datetime import date, timedelta
from calendar import monthrange
from rest_framework import viewsets
from lsdb.models import AssetCalibration
from rest_framework.response import Response
from rest_framework.decorators import action


class AssetCalibrationEmailViewSet(viewsets.ModelViewSet):

    @action(detail=False, methods=['get'])
    def asset_list(self, request):
        date_input = request.query_params.get('date')
        all_flag = request.query_params.get('all')
        all_flag = str(all_flag).lower() == "true"
        if all_flag and date_input:
            return Response({"error": "Do not pass date when all=true"}, status=400)
        if not all_flag and not date_input:
            return Response({"error": "date is required when all=false"}, status=400)
        ranges = []
        if all_flag:
            today = date.today()
            curr_start = date(today.year, today.month, 1)
            curr_end = date(today.year, today.month, monthrange(today.year, today.month)[1])
            prev_month = today.month - 1 or 12
            prev_year = today.year if today.month != 1 else today.year - 1
            prev_start = date(prev_year, prev_month, 1)
            prev_end = date(prev_year, prev_month, monthrange(prev_year, prev_month)[1])
            ranges.extend([
                (prev_start, prev_end),
                (curr_start, curr_end)
            ])
        else:
            try:
                year, month = map(int, date_input.split('-'))
            except:
                return Response({"error": "Invalid date format. Use YYYY-MM"}, status=400)
            start_date = date(year, month, 1)
            end_date = date(year, month, monthrange(year, month)[1])
            ranges.append((start_date, end_date))
        queryset = AssetCalibration.objects.all()
        result = []
        for obj in queryset:
            if obj.last_calibrated_date and obj.schedule_for_calibration:
                next_date = (obj.last_calibrated_date + timedelta(days=obj.schedule_for_calibration)).date()
                for start_date, end_date in ranges:
                    if start_date <= next_date <= end_date:
                        result.append({
                            "id": obj.id,
                            "asset_name": obj.asset_name,
                            "asset_number": obj.asset_number,
                            "last_calibrated_date": obj.last_calibrated_date,
                            "schedule_for_calibration": obj.schedule_for_calibration,
                            "next_calibration_date": next_date
                        })
                        break
        result.sort(key=lambda x: x['next_calibration_date'])
        return Response({"data": result})