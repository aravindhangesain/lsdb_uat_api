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
        month_input = request.query_params.get('month')
        year = request.query_params.get('year')
        if not month_input or not year:
            return Response({"error": "month and year are required"},status=400)
        month_map = {m.lower(): i for i, m in enumerate(calendar.month_name) if m}
        month_map.update({m.lower(): i for i, m in enumerate(calendar.month_abbr) if m})
        try:
            if month_input.isdigit():
                month = int(month_input)
            else:
                month = month_map.get(month_input.lower())
            if not month or month < 1 or month > 12:
                raise ValueError
        except:
            return Response({"error": "Invalid month"}, status=400)
        year = int(year)
        start_date = date(year, month, 1)
        end_date = date(year, month, monthrange(year, month)[1])
        queryset = AssetCalibration.objects.all()
        result = []
        for obj in queryset:
            if obj.last_calibrated_date and obj.schedule_for_calibration:
                next_date = (obj.last_calibrated_date + timedelta(days=obj.schedule_for_calibration)).date()
                if start_date <= next_date <= end_date:
                    result.append({
                        "id": obj.id,
                        "asset_name": obj.asset_name,
                        "asset_number": obj.asset_number,
                        "last_calibrated_date": obj.last_calibrated_date,
                        "schedule_for_calibration": obj.schedule_for_calibration,
                        "next_calibration_date": next_date
                    })
        result.sort(key=lambda x: x['next_calibration_date'])
        return Response({"data": result})