import json
import magic
import pandas as pd

from rest_framework import serializers
from django.db.models import Q
from lsdb.models import Asset, AssetCalibration, ProcedureResult, StepResult, StressRunResult, Unit, UnitType, ModuleProperty,WorkOrder
from lsdb.models import MeasurementResult, MeasurementCorrectionFactor
from lsdb.models import ProcedureResult_FinalResult
from lsdb.serializers.StepResultSerializer import StepResultSerializer
from lsdb.serializers.StepResultSerializer import StepResultStressSerializer
from lsdb.serializers.UnitTypeSerializer import UnitTypeSerializer
from django.db import connection

from lsdb.serializers.AssetCalibrationSerializer import AssetCalibrationSerializer

# class IVCurveMeasurementSerializer(serializers.HyperlinkedModelSerializer):
#     ### DEPRECATED
#     # KLUGE: This opens and closes the same file twice. which is lame
#     color = serializers.SerializerMethodField()
#     chart = serializers.SerializerMethodField()
#     multiplier = serializers.SerializerMethodField()
#
#     def get_multiplier(self,obj):
#         # print('curve_mult')
#         if obj.result_files.all():
#             multiplier = 0
#             for file in obj.result_files.all():
#                 # print(file.file.name)
#                 file_handle = file.file.open('rb')
#                 if magic.from_buffer(file_handle.read(2048), mime=True) != 'text/plain':
#                     # It's binary, we can't eat that(mfr files show up as: application/x-wine-extension-ini)
#                     continue
#                 file_handle.seek(0)
#                 data_table = pd.read_csv(file_handle, sep='\t')
#                 # Check that this is a sinton or pasan text file
#                 if 'Vcorr' in data_table.columns:
#                     multiplier = float(int(data_table.iat[0,12]) / 1000)
#                     return multiplier
#                 elif 'Model_Voltage_(V)' in data_table.columns:
#                     # this is not the file we're looking for
#                     continue
#                 else:
#                     file_handle.seek(0)
#                     data_table = pd.read_csv(file_handle, sep='\t')
#                     # print(data_table.columns)
#                     if 'Power_per_Sun_(W/m2)' in data_table.columns:
#                         multiplier = data_table['Power_per_Sun_(W/m2)'][0] * data_table['Intensity_(suns)'][0] / 1000
#                 file_handle.close()
#             # print('MULT',multiplier)
#             return multiplier
#         else:
#             return({})
#
#     def get_color(self,obj): return "hsl(263, 70%, 50%)"
#
#     def get_chart(self, obj):
#         # print('files:',obj.id)
#         # KLUGE: This has zero exception handling
#         if obj.result_files.all():
#             # We have a file to work on:
#             foo = 0
#             for file in obj.result_files.all():
#                 # print(file.file.name)
#                 # need to detect file type here:
#                 file_handle = file.file.open('rb')
#                 if magic.from_buffer(file_handle.read(2048), mime=True) != 'text/plain':
#                     # It's binary, we can't eat that(mfr files show up as: application/x-wine-extension-ini)
#                     continue
#                 file_handle.seek(0)
#                 data_table = pd.read_csv(file_handle, sep='\t')
#                 file_handle.close()
#                 # Check that this is a sinton or pasan text file
#                 # print(data_table.columns)
#                 if 'Vcorr' in data_table.columns:
#                     # Pasan
#                     cols = data_table[['Vcorr','Icorr']]
#                 elif 'Model_Voltage_(V)' in data_table.columns:
#                     # Sinton
#                     cols = data_table[['Model_Voltage_(V)','Model_Current_(A)']]
#                 else:
#                     # None of the above:
#                     continue
#                 cols.columns= ['x', 'y']
#                 foo = cols.to_json(orient='records')
#             if foo:
#                 return (json.loads(foo))
#         # file measurement without files
#         return([])
#
#     class Meta:
#         model = MeasurementResult
#         fields = [
#             'id',
#             'color',
#             'multiplier',
#             'chart',
#         ]

class TransformIVCurveSerializer(serializers.HyperlinkedModelSerializer):
    # test_sequence_definition_name = serializers.ReadOnlyField(source='test_sequence_definition.name')
    procedure_definition_name = serializers.ReadOnlyField(source='procedure_definition.name')
    # disposition_name = serializers.SerializerMethodField()
    # visualizer = serializers.ReadOnlyField(source='procedure_definition.visualizer.name')
    unit_type = UnitTypeSerializer(source='unit.unit_type', many=False)
    flash_values = serializers.SerializerMethodField()
    iv_curves = serializers.SerializerMethodField()
    assets = serializers.SerializerMethodField()
    # multiplier = serializers.SerializerMethodField()
    has_notes = serializers.SerializerMethodField()
    open_notes = serializers.SerializerMethodField()
    final_result = serializers.SerializerMethodField()
    last_calibration_date = serializers.SerializerMethodField()
    retest_reasons = serializers.SerializerMethodField()

    asset_details = serializers.SerializerMethodField()
    calibrated_during_test= serializers.SerializerMethodField()

    def get_calibrated_during_test(self,obj):
        calibrated_during_test=StressRunResult.objects.filter(procedure_result_id=obj.id,stress_name='Test Start').first()
        if calibrated_during_test:
            return calibrated_during_test.is_calibrated
        else:
            return None
    
    def get_asset_details(self, obj):
        request = self.context.get('request')

        step_result = StepResult.objects.filter(
            procedure_result_id=obj.id
        ).first()

        if not step_result:
            return None

        measurement = MeasurementResult.objects.filter(
            step_result_id=step_result.id
        ).first()

        if not measurement:
            return None

        asset = AssetCalibration.objects.filter(
            asset_id=measurement.asset_id
        ).first()

        if not asset:
            return None

        serializer = AssetCalibrationSerializer(
            asset,
            context={'request': request}
        )

        return serializer.data

    

    def get_has_notes(self, obj):
        if obj.notes.count() > 0:
            return True
        else:
            return False

    def get_final_result(self, instance):
        try:
            final_result_value = ProcedureResult_FinalResult.objects.get(procedure_result_id=instance.id)
            return final_result_value.final_result
        except ProcedureResult_FinalResult.DoesNotExist:
            return None

    def get_open_notes(self, obj):
        if obj.notes.filter(Q(disposition__complete=False) | Q(disposition__isnull=True)).count() > 0:
            return True
        else:
            return False

    def get_multiplier(self, obj):
        # Stubbed deliberately --MD
        # print('in mult')
        # flash_measurements = MeasurementResult.objects.filter(
        #     step_result__in=obj.stepresult_set.all(),
        #     measurement_result_type__name__icontains='result_double'
        # )
        flash = {}
        # for measurement in flash_measurements:
        #     flash[measurement.name] = measurement.result_double
        return (flash)

    def get_flash_values(self, obj):
        # print('in flash')
        # TODO: This should suppress failing measurements
        flash_measurements = MeasurementResult.objects.filter(
            step_result__in=obj.stepresult_set.all(),
            measurement_result_type__name__icontains='result_double'
        )
        flash = {}
        for measurement in flash_measurements:
            flash[measurement.name] = measurement.result_double
        return (flash)

    def parse_flash(self, file):
        mult = None
        # print(file.file.name)
        file_handle = file.file.open('rb')
        if magic.from_buffer(file_handle.read(2048), mime=True) != 'text/plain':
            # It's binary, we can't eat that(mfr files show up as: application/x-wine-extension-ini)
            # print('binary')
            file_handle.close()
            return None, None, None
        file_handle.seek(0)
        # print('about to read')
        import traceback
        try:
            data_table = pd.read_csv(file_handle, sep='\t', encoding_errors='ignore')
            # maybe have a different seprator?
            if len(data_table.columns.array) <= 1:
                file_handle.seek(0)
                data_table = pd.read_csv(file_handle, sep=';', encoding_errors='ignore', skiprows=12)
            # print(data_table.columns)
        except Exception as err:
            print(Exception)
            print(err)
            traceback.print_tb(err.__traceback__)

        # print(data_table)
        # Check that this is a sinton or pasan text file
        if 'Vcorr' in data_table.columns:
            # pasan chart....
            mult = float(int(data_table.iat[0, 12]) / 1000)
            # print('pasandata')
            cols = data_table[['Vcorr', 'Icorr']]
            filetype = 'pdata'
        elif 'Nr' in data_table.columns:
            # Looks like a HALM file, make it look like a PASAN file
            cols = data_table[['Ucor [[V]]', 'Icor [[A]]']]
            cols.columns = ['Vcorr', 'Icorr']
            filetype = 'pdata'
        elif 'Model_Voltage_(V)' in data_table.columns:
            # sinton data file
            # print('sinton data')
            cols = data_table[['Model_Voltage_(V)', 'Model_Current_(A)', 'Vload_(V)', 'ILoad_(A)']]
            filetype = 'sdata'
        else:
            # print('sinton params')
            if 'Power_per_Sun_(W/m2)' in data_table.columns:
                cols = data_table['Power_per_Sun_(W/m2)'][0] * data_table['Intensity_(suns)'][0] / 1000
                filetype = 'sparams'
        file_handle.close()
        return filetype, cols, mult

    def get_iv_curves(self, obj):
        measurements = MeasurementResult.objects.filter(
            step_result__in=obj.stepresult_set.all(),
            measurement_result_type__name__icontains='result_files',
            disposition__isnull=False
        ).exclude(
            disposition__name__icontains='fail'
        )
        iv_curves = []
        temp_curve = {}  # split sinton holding dict
        # print('get_iv',measurements)
        # print('count',measurements.count())
        try:
            for measurement in measurements:
                # print(measurement.id)
                if measurement.result_files.all().count() == 1:  # Pasan or split-sinton
                    curve_dict = {}
                    # print('have 1 measurement')
                    curve_dict['id'] = measurement.id
                    curve_dict['color'] = "hsl(263, 70%, 50%)"
                    curve_dict['multiplier'] = 0
                    # for file in measurement.result_files.all():
                    filetype, cols, mult = self.parse_flash(measurement.result_files.first())
                    # print('uno')
                    if filetype == 'sparams':  # sinton params,
                        temp_curve['multiplier'] = cols
                        temp_curve['color'] = "hsl(263, 70%, 50%)"
                    if filetype == 'sdata':  # sinton data,
                        temp_curve['id'] = measurement.id
                        curve_one = cols[['Model_Voltage_(V)', 'Model_Current_(A)']]
                        curve_two = cols[['Vload_(V)', 'ILoad_(A)']]
                        curve_one.columns = ['x', 'y']
                        curve_two.columns = ['x', 'y']
                        temp_curve['curve_one'] = json.loads(curve_one.to_json(orient='records'))
                        temp_curve['curve_two'] = json.loads(curve_two.to_json(orient='records'))
                    if filetype == 'pdata':  # pasan data,
                        cols.columns = ['x', 'y']
                        json_points = cols.to_json(orient='records')
                        curve_dict['multiplier'] = mult
                        curve_dict['chart'] = json.loads(json_points)
                        iv_curves.append(curve_dict)

                elif measurement.result_files.all().count() > 1:  # multi-file, probably sinton
                    curve_dict = {}
                    curve_dict['id'] = measurement.id
                    curve_dict['color'] = "hsl(263, 70%, 50%)"
                    curve_dict['multiplier'] = 0
                    # print('ganged sinton')
                    for file in measurement.result_files.all():
                        filetype, data, mult = self.parse_flash(file)
                        if filetype == None:
                            # that was binary, ignore it.
                            continue
                        if filetype == 'sparams':  # sinton params,
                            curve_dict['multiplier'] = data
                            curve_dict['color'] = "hsl(263, 70%, 50%)"
                        if filetype == 'sdata':  # sinton data,
                            cols = data
                    # done parsing files
                    if 'Model_Voltage_(V)' in cols.columns:
                        # sinton - multi
                        bonus_dict = {}
                        bonus_dict['id'] = '{}-A'.format(measurement.id)
                        bonus_dict['color'] = "hsl(263, 70%, 50%)"
                        bonus_dict['multiplier'] = curve_dict['multiplier']

                        curve_one = cols[['Model_Voltage_(V)', 'Model_Current_(A)']]
                        curve_two = cols[['Vload_(V)', 'ILoad_(A)']]
                        curve_one.columns = ['x', 'y']
                        curve_two.columns = ['x', 'y']

                        curve_dict['chart'] = json.loads(curve_one.to_json(orient='records'))
                        bonus_dict['chart'] = json.loads(curve_two.to_json(orient='records'))

                        iv_curves.append(curve_dict)
                        iv_curves.append(bonus_dict)

            # Pasan cases hould be done, but if we get here and iv_curves is empty we need sinton:
            if not len(iv_curves):
                # print('unsplitting sinton!')
                curve_dict = {}
                bonus_dict = {}

                curve_dict['id'] = '{}'.format(measurement.id)
                bonus_dict['id'] = '{}-A'.format(measurement.id)

                curve_dict['color'] = temp_curve['color']
                bonus_dict['color'] = temp_curve['color']

                curve_dict['multiplier'] = temp_curve['multiplier']
                bonus_dict['multiplier'] = temp_curve['multiplier']

                curve_dict['chart'] = temp_curve['curve_one']
                bonus_dict['chart'] = temp_curve['curve_two']

                iv_curves.append(curve_dict)
                iv_curves.append(bonus_dict)
            # print('curves:',iv_curves)
        except:
            # Something failed and we need a fake result, probably "no files"
            measurements = MeasurementResult.objects.filter(
                step_result__in=obj.stepresult_set.all(),
                name__icontains='irradiance',
                disposition__isnull=False
            ).exclude(
                disposition__name__icontains='fail'
            )
            if len(measurements):
                measurement = measurements.first()
                iv_curves.append(
                    {
                        'id': measurement.id,
                        'multiplier': getattr(measurement, measurement.measurement_result_type.name) / 1000,
                        "color": "hsl(263, 70%, 50%)",
                        "chart": [{
                            "x": 0,
                            "y": 0
                        }]
                    }
                )
            else:
                # Completely fake:
                iv_curves.append(
                    {
                        'id': 0,
                        'multiplier': 1,
                        "color": "hsl(263, 70%, 50%)",
                        "chart": [{
                            "x": 0,
                            "y": 0
                        }]
                    }
                )
            pass
        return iv_curves

    def get_disposition_name(self, obj):
        # print('in disp')
        if obj.disposition:
            return obj.disposition.name
        else:
            return None

    def get_assets(self, obj):
        measurements = MeasurementResult.objects.filter(
            step_result__in=obj.stepresult_set.all(),
            disposition__isnull=False,
        ).distinct().values_list('asset__name')
        assets = set(measurements)
        return assets
    
    def get_last_calibration_date(self, obj):
        measurements = (
            MeasurementResult.objects
            .filter(
                step_result__in=obj.stepresult_set.all(),
                disposition__isnull=False,
                asset__isnull=False,
                asset__name__isnull=False
            )
            .values_list('asset__name', flat=True)
            .distinct()
        )

        assets = set(measurements)
        last_calibration_date = []

        for asset_name in assets:
            # safer: won't raise if asset is missing
            asset = Asset.objects.filter(name=asset_name).first()
            if not asset:
                continue  # skip if no matching Asset

            measurement_result = (
                MeasurementResult.objects
                .filter(
                    step_result_id__in=obj.stepresult_set.all(),
                    asset_id=asset.id
                )
                .order_by('-date_time')
                .first()
            )

            if measurement_result and measurement_result.date_time:
                last_calibration_date.append(measurement_result.date_time)

        return last_calibration_date

    def get_retest_reasons(self, obj):
        try:
            retest_reasons_qs = obj.retestprocedures_set.all()
            reasons = []
            for reason in retest_reasons_qs:
                reasons.append({
                    'id': reason.id,
                    'retestreason': reason.retestreason.reason,
                    'short_name': reason.retestreason.description,
                    'updated_by': reason.updated_by.username if reason.updated_by else None,
                    'date_time': reason.datetime,
                })
            return reasons
        except:
            return []
        
    class Meta:
        model = ProcedureResult
        fields = [
            'id',
            'url',
            'unit',
            'procedure_definition_name',
            'disposition',
            'name',
            'unit_type',
            'flash_values',
            'iv_curves',
            'assets',
            'last_calibration_date',
            'has_notes',
            'open_notes',
            'final_result',
            'retest_reasons',
            'asset_details',
            'calibrated_during_test'
        ]


class ProcedureResultSerializer(serializers.HyperlinkedModelSerializer):
    step_results = StepResultSerializer(source='stepresult_set', many=True, read_only=True)
    work_order_name = serializers.ReadOnlyField(source='work_order.name')
    customer_name = serializers.ReadOnlyField(source='work_order.project.customer.name')
    project_number = serializers.ReadOnlyField(source='work_order.project.number')
    test_sequence_definition_name = serializers.ReadOnlyField(source='test_sequence_definition.name')
    procedure_definition_name = serializers.ReadOnlyField(source='procedure_definition.name')
    disposition_name = serializers.SerializerMethodField()
    visualizer = serializers.ReadOnlyField(source='procedure_definition.visualizer.name')
    assets = serializers.SerializerMethodField()
    has_notes = serializers.SerializerMethodField()
    open_notes = serializers.SerializerMethodField()
    final_result = serializers.SerializerMethodField()
    last_calibration_date = serializers.SerializerMethodField()
    retest_reasons = serializers.SerializerMethodField()
    asset_details = serializers.SerializerMethodField()
    calibrated_during_test= serializers.SerializerMethodField()

    def get_calibrated_during_test(self,obj):
        calibrated_during_test=StressRunResult.objects.filter(procedure_result_id=obj.id,stress_name='Test Start').first()
        if calibrated_during_test:
            return calibrated_during_test.is_calibrated
        else:
            return None
    
    def get_asset_details(self, obj):
        request = self.context.get('request')

        step_result = StepResult.objects.filter(
            procedure_result_id=obj.id
        ).first()

        if not step_result:
            return None

        measurement = MeasurementResult.objects.filter(
            step_result_id=step_result.id
        ).first()

        if not measurement:
            return None

        asset = AssetCalibration.objects.filter(
            asset_id=measurement.asset_id
        ).first()

        if not asset:
            return None

        serializer = AssetCalibrationSerializer(
            asset,
            context={'request': request}
        )

        return serializer.data

    def get_has_notes(self, obj):
        if obj.notes.count() > 0:
            return True
        else:
            return False

    def get_final_result(self, instance):
        try:
            final_result_value = ProcedureResult_FinalResult.objects.get(procedure_result_id=instance.id)
            return final_result_value.final_result
        except ProcedureResult_FinalResult.DoesNotExist:
            return None

    def get_open_notes(self, obj):
        if obj.notes.filter(Q(disposition__complete=False) | Q(disposition__isnull=True)).count() > 0:
            return True
        else:
            return False

    def get_disposition_name(self, obj):
        if obj.disposition:
            return obj.disposition.name
        else:
            return None

    def get_assets(self, obj):
        measurements = MeasurementResult.objects.filter(
            step_result__in=obj.stepresult_set.all(),
            disposition__isnull=False,
        ).distinct().values_list('asset__name')
        assets = set(measurements)
        return assets
    
    def get_last_calibration_date(self, obj):
        measurements = (
            MeasurementResult.objects
            .filter(
                step_result__in=obj.stepresult_set.all(),
                disposition__isnull=False,
                asset__isnull=False,
                asset__name__isnull=False
            )
            .values_list('asset__name', flat=True)
            .distinct()
        )

        assets = set(measurements)
        last_calibration_date = []

        for asset_name in assets:
            # safer: won't raise if asset is missing
            asset = Asset.objects.filter(name=asset_name).first()
            if not asset:
                continue  # skip if no matching Asset

            measurement_result = (
                MeasurementResult.objects
                .filter(
                    step_result_id__in=obj.stepresult_set.all(),
                    asset_id=asset.id
                )
                .order_by('-date_time')
                .first()
            )

            if measurement_result and measurement_result.date_time:
                last_calibration_date.append(measurement_result.date_time)

        return last_calibration_date
    
    def get_retest_reasons(self, obj):
        try:
            retest_reasons_qs = obj.retestprocedures_set.all()
            reasons = []
            for reason in retest_reasons_qs:
                reasons.append({
                    'id': reason.id,
                    'retestreason': reason.retestreason.reason,
                    'short_name': reason.retestreason.description,
                    'updated_by': reason.updated_by.username if reason.updated_by else None,
                    'date_time': reason.datetime,
                })
            return reasons
        except:
            return []
                


    class Meta:
        model = ProcedureResult
        fields = [
            'id',
            'url',
            'unit',
            'procedure_definition',
            'procedure_definition_name',
            'disposition',
            'disposition_name',
            'start_datetime',
            'end_datetime',
            'customer_name',
            'project_number',
            'work_order',
            'work_order_name',
            'linear_execution_group',
            'name',
            'work_in_progress_must_comply',
            'group',
            'supersede',
            'version',
            'test_sequence_definition',
            'test_sequence_definition_name',
            'allow_skip',
            'step_results',
            'visualizer',
            'assets',
            'last_calibration_date',
            'asset_details',
            'calibrated_during_test',
            'has_notes',
            'open_notes',
            'final_result',
            'retest_reasons'
        ]


class ProcedureResultStressSerializer(serializers.HyperlinkedModelSerializer):
    step_results = StepResultStressSerializer(source='stepresult_set', many=True, read_only=True)
    work_order_name = serializers.ReadOnlyField(source='work_order.name')
    customer_name = serializers.ReadOnlyField(source='work_order.project.customer.name')
    project_number = serializers.ReadOnlyField(source='work_order.project.number')
    test_sequence_definition_name = serializers.ReadOnlyField(source='test_sequence_definition.name')
    procedure_definition_name = serializers.ReadOnlyField(source='procedure_definition.name')
    disposition_name = serializers.SerializerMethodField()
    visualizer = serializers.ReadOnlyField(source='procedure_definition.visualizer.name')
    assets = serializers.SerializerMethodField()
    has_notes = serializers.SerializerMethodField()
    open_notes = serializers.SerializerMethodField()
    final_result = serializers.SerializerMethodField()
    last_calibration_date = serializers.SerializerMethodField()

    asset_details = serializers.SerializerMethodField()
    calibrated_during_test= serializers.SerializerMethodField()

    def get_calibrated_during_test(self,obj):
        calibrated_during_test=StressRunResult.objects.filter(procedure_result_id=obj.id,stress_name='Test Start').first()
        if calibrated_during_test:
            return calibrated_during_test.is_calibrated
        else:
            return None
    
    def get_asset_details(self, obj):
        request = self.context.get('request')

        step_result = StepResult.objects.filter(
            procedure_result_id=obj.id
        ).first()

        if not step_result:
            return None

        measurement = MeasurementResult.objects.filter(
            step_result_id=step_result.id
        ).first()

        if not measurement:
            return None

        asset = AssetCalibration.objects.filter(
            asset_id=measurement.asset_id
        ).first()

        if not asset:
            return None

        serializer = AssetCalibrationSerializer(
            asset,
            context={'request': request}
        )

        return serializer.data

    def get_has_notes(self, obj):
        if obj.notes.count() > 0:
            return True
        else:
            return False

    def get_final_result(self, instance):
        try:
            final_result_value = ProcedureResult_FinalResult.objects.get(procedure_result_id=instance.id)
            return final_result_value.final_result
        except ProcedureResult_FinalResult.DoesNotExist:
            return None

    def get_open_notes(self, obj):
        if obj.notes.filter(Q(disposition__complete=False) | Q(disposition__isnull=True)).count() > 0:
            return True
        else:
            return False

    def get_disposition_name(self, obj):
        if obj.disposition:
            return obj.disposition.name
        else:
            return None

    def get_assets(self, obj):
        measurements = MeasurementResult.objects.filter(
            step_result__in=obj.stepresult_set.all(),
            disposition__isnull=False,
        ).distinct().values_list('asset__name')
        assets = set(measurements)
        return assets
    
    def get_last_calibration_date(self, obj):

        step_results=StepResult.objects.filter(procedure_result_id=obj.id,name__in=['Test Start','Test Resume'])

        for step in step_results:
            if step.name=='Test Resume':
                measurement=MeasurementResult.objects.get(step_result_id=step.id)
                if measurement and measurement.result_datetime:
                    return [measurement.result_datetime]
                else:
                    continue
            elif step.name=='Test Start':
                measurement=MeasurementResult.objects.get(step_result_id=step.id)
                if measurement and measurement.result_datetime:
                    return [measurement.result_datetime]
        return None
                
        
                
    class Meta:
        model = ProcedureResult
        fields = [
            'id',
            'url',
            'unit',
            'procedure_definition',
            'procedure_definition_name',
            'disposition',
            'disposition_name',
            'start_datetime',
            'end_datetime',
            'customer_name',
            'project_number',
            'work_order',
            'work_order_name',
            'linear_execution_group',
            'name',
            'work_in_progress_must_comply',
            'group',
            'supersede',
            'version',
            'test_sequence_definition',
            'test_sequence_definition_name',
            'allow_skip',
            'step_results',
            'visualizer',
            'assets',
            'last_calibration_date',
            'asset_details',
            'calibrated_during_test',
            'has_notes',
            'open_notes',
            'final_result'
        ]


class FailedProjectReportSerializer(serializers.HyperlinkedModelSerializer):
    work_order_name = serializers.ReadOnlyField(source='work_order.name')
    unit_serial_number = serializers.ReadOnlyField(source='unit.serial_number')
    project_number = serializers.ReadOnlyField(source='work_order.project.number')
    test_sequence_definition_name = serializers.ReadOnlyField(source='test_sequence_definition.name')
    procedure_definition_name = serializers.ReadOnlyField(source='procedure_definition.name')
    description = serializers.ReadOnlyField(source='test_sequence_definition.description')
    disposition_name = serializers.SerializerMethodField()
    customer_name = serializers.ReadOnlyField(source='work_order.project.customer.name')
    note_id = serializers.SerializerMethodField()
    note_text = serializers.SerializerMethodField()
    note_subject  = serializers.SerializerMethodField()
    notes = serializers.SerializerMethodField()
    note_attachment_id = serializers.SerializerMethodField()
    asset_details = serializers.SerializerMethodField()
    calibrated_during_test= serializers.SerializerMethodField()

    def get_calibrated_during_test(self,obj):
        calibrated_during_test=StressRunResult.objects.filter(procedure_result_id=obj.id,stress_name='Test Start').first()
        if calibrated_during_test:
            return calibrated_during_test.is_calibrated
        else:
            return None
    
    def get_asset_details(self, obj):
        request = self.context.get('request')

        step_result = StepResult.objects.filter(
            procedure_result_id=obj.id
        ).first()

        if not step_result:
            return None

        measurement = MeasurementResult.objects.filter(
            step_result_id=step_result.id
        ).first()

        if not measurement:
            return None

        asset = AssetCalibration.objects.filter(
            asset_id=measurement.asset_id
        ).first()

        if not asset:
            return None

        serializer = AssetCalibrationSerializer(
            asset,
            context={'request': request}
        )

        return serializer.data

    def get_note_attachment_id(self, obj):
        note_id = self.get_note_id(obj)
        if not note_id:
            return []
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT azurefile_id FROM lsdb_note_attachments WHERE note_id = %s
            """, [note_id])
            return [row[0] for row in cursor.fetchall()] 


    def get_disposition_name(self, obj):
        if obj.disposition:
            return obj.disposition.name
        else:
            return None
        
    def get_note_id(self, obj):
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT un.note_id 
                FROM lsdb_unit_notes un 
                JOIN lsdb_note n ON un.note_id = n.id 
                WHERE n.note_type_id = 3 AND un.unit_id = %s
                LIMIT 1
            """, [obj.unit_id])
            result = cursor.fetchone()
        return result[0] if result else None
    
    def get_note_text(self, obj):
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT n.text 
                FROM lsdb_unit_notes un 
                JOIN lsdb_note n ON un.note_id = n.id 
                WHERE n.note_type_id = 3 AND un.unit_id = %s
                LIMIT 1
            """, [obj.unit_id])
            result = cursor.fetchone()
        return result[0].replace("\n", " ") if result else None
    
    def get_note_subject(self, obj):
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT n.subject
                FROM lsdb_unit_notes un 
                JOIN lsdb_note n ON un.note_id = n.id 
                WHERE n.note_type_id = 3 AND un.unit_id = %s
                LIMIT 1
            """, [obj.unit_id])
            result = cursor.fetchone()
        return result[0] if result else None
    

    def get_notes(self, obj):
        """Fetches and appends notes with the required fields."""
        if not obj.unit_id:
            return []
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT n.id, n.user_id, u.username, n.owner_id, o.username AS owner_name, 
                       n.subject, n.text, n.note_type_id, nt.name AS note_type_name, 
                       n.disposition_id, d.name AS disposition_name
                FROM lsdb_note n
                JOIN lsdb_unit_notes un ON n.id = un.note_id
                JOIN auth_user u ON n.user_id = u.id
                JOIN auth_user o ON n.owner_id = o.id
                JOIN lsdb_notetype nt ON n.note_type_id = nt.id
                JOIN lsdb_disposition d ON n.disposition_id = d.id
                WHERE un.unit_id = %s
            """, [obj.unit_id])
            notes_data = [
                {
                    "id": row[0],
                    "user": row[1],
                    "username": row[2],
                    "owner": row[3],
                    "owner_name": row[4],
                    "subject": row[5],
                    "text": row[6],
                    "note_type": row[7],
                    "note_type_name": row[8],
                    "disposition": row[9],
                    "disposition_name": row[10],
                }
                for row in cursor.fetchall()
            ]
        return notes_data
    
    


    class Meta:
        model = ProcedureResult
        fields = [
            'id',
            'url',
            'name',
            'unit',
            'unit_serial_number',
            'procedure_definition',
            'procedure_definition_name',
            'disposition',
            'disposition_name',
            'start_datetime',
            'end_datetime',
            'project_number',
            'work_order',
            'work_order_name',
            'test_sequence_definition',
            'test_sequence_definition_name',
            'description',
            'customer_name',
            'note_id',
            'note_text',
            'note_subject',
            'note_attachment_id',
            'notes',
            'asset_details',
            'calibrated_during_test'
            
        ]

class RetestReportListSerializer(serializers.HyperlinkedModelSerializer):
    work_order_name = serializers.ReadOnlyField(source='work_order.name')
    unit_serial_number = serializers.ReadOnlyField(source='unit.serial_number')
    project_number = serializers.ReadOnlyField(source='work_order.project.number')
    test_sequence_definition_name = serializers.ReadOnlyField(source='test_sequence_definition.name')
    procedure_definition_name = serializers.ReadOnlyField(source='procedure_definition.name')
    description = serializers.ReadOnlyField(source='test_sequence_definition.description')
    disposition_name = serializers.SerializerMethodField()
    customer_name = serializers.ReadOnlyField(source='work_order.project.customer.name')
    asset_details = serializers.SerializerMethodField()
    calibrated_during_test= serializers.SerializerMethodField()

    def get_calibrated_during_test(self,obj):
        calibrated_during_test=StressRunResult.objects.filter(procedure_result_id=obj.id,stress_name='Test Start').first()
        if calibrated_during_test:
            return calibrated_during_test.is_calibrated
        else:
            return None
    
    def get_asset_details(self, obj):
        request = self.context.get('request')

        step_result = StepResult.objects.filter(
            procedure_result_id=obj.id
        ).first()

        if not step_result:
            return None

        measurement = MeasurementResult.objects.filter(
            step_result_id=step_result.id
        ).first()

        if not measurement:
            return None

        asset = AssetCalibration.objects.filter(
            asset_id=measurement.asset_id
        ).first()

        if not asset:
            return None

        serializer = AssetCalibrationSerializer(
            asset,
            context={'request': request}
        )

        return serializer.data
    # note_id = serializers.SerializerMethodField()
    # note_text = serializers.SerializerMethodField()
    # note_subject  = serializers.SerializerMethodField()
    # notes = serializers.SerializerMethodField()
    # note_attachment_id = serializers.SerializerMethodField()

    # def get_note_attachment_id(self, obj):
    #     note_id = self.get_note_id(obj)
    #     if not note_id:
    #         return []
    #     with connection.cursor() as cursor:
    #         cursor.execute("""
    #             SELECT azurefile_id FROM lsdb_note_attachments WHERE note_id = %s
    #         """, [note_id])
    #         return [row[0] for row in cursor.fetchall()] 


    def get_disposition_name(self, obj):
        if obj.disposition:
            return obj.disposition.name
        else:
            return None
        
    # def get_note_id(self, obj):
    #     with connection.cursor() as cursor:
    #         cursor.execute("""
    #             SELECT un.note_id 
    #             FROM lsdb_unit_notes un 
    #             JOIN lsdb_note n ON un.note_id = n.id 
    #             WHERE n.note_type_id = 3 AND un.unit_id = %s
    #             LIMIT 1
    #         """, [obj.unit_id])
    #         result = cursor.fetchone()
    #     return result[0] if result else None
    
    # def get_note_text(self, obj):
    #     with connection.cursor() as cursor:
    #         cursor.execute("""
    #             SELECT n.text 
    #             FROM lsdb_unit_notes un 
    #             JOIN lsdb_note n ON un.note_id = n.id 
    #             WHERE n.note_type_id = 3 AND un.unit_id = %s
    #             LIMIT 1
    #         """, [obj.unit_id])
    #         result = cursor.fetchone()
    #     return result[0].replace("\n", " ") if result else None
    
    # def get_note_subject(self, obj):
    #     with connection.cursor() as cursor:
    #         cursor.execute("""
    #             SELECT n.subject
    #             FROM lsdb_unit_notes un 
    #             JOIN lsdb_note n ON un.note_id = n.id 
    #             WHERE n.note_type_id = 3 AND un.unit_id = %s
    #             LIMIT 1
    #         """, [obj.unit_id])
    #         result = cursor.fetchone()
    #     return result[0] if result else None
    

    # def get_notes(self, obj):
    #     """Fetches and appends notes with the required fields."""
    #     if not obj.unit_id:
    #         return []
    #     with connection.cursor() as cursor:
    #         cursor.execute("""
    #             SELECT n.id, n.user_id, u.username, n.owner_id, o.username AS owner_name, 
    #                    n.subject, n.text, n.note_type_id, nt.name AS note_type_name, 
    #                    n.disposition_id, d.name AS disposition_name
    #             FROM lsdb_note n
    #             JOIN lsdb_unit_notes un ON n.id = un.note_id
    #             JOIN auth_user u ON n.user_id = u.id
    #             JOIN auth_user o ON n.owner_id = o.id
    #             JOIN lsdb_notetype nt ON n.note_type_id = nt.id
    #             JOIN lsdb_disposition d ON n.disposition_id = d.id
    #             WHERE un.unit_id = %s
    #         """, [obj.unit_id])
    #         notes_data = [
    #             {
    #                 "id": row[0],
    #                 "user": row[1],
    #                 "username": row[2],
    #                 "owner": row[3],
    #                 "owner_name": row[4],
    #                 "subject": row[5],
    #                 "text": row[6],
    #                 "note_type": row[7],
    #                 "note_type_name": row[8],
    #                 "disposition": row[9],
    #                 "disposition_name": row[10],
    #             }
    #             for row in cursor.fetchall()
    #         ]
    #     return notes_data
    
    


    class Meta:
        model = ProcedureResult
        fields = [
            'id',
            'url',
            'name',
            'unit',
            'unit_serial_number',
            'procedure_definition',
            'procedure_definition_name',
            'disposition',
            'disposition_name',
            'start_datetime',
            'end_datetime',
            'project_number',
            'work_order',
            'work_order_name',
            'test_sequence_definition',
            'test_sequence_definition_name',
            'description',
            'customer_name',
            'group_id'
            'asset_details',
            'calibrated_during_test'
            # 'note_id',
            # 'note_text',
            # 'note_subject',
            # 'note_attachment_id',
            # 'notes',
            
        ]


class FlashTestSerializer(serializers.HyperlinkedModelSerializer):
    work_order_name = serializers.ReadOnlyField(source='work_order.name')
    unit_serial_number = serializers.ReadOnlyField(source='unit.serial_number')
    project_number = serializers.ReadOnlyField(source='work_order.project.number')
    test_sequence_definition_name = serializers.ReadOnlyField(source='test_sequence_definition.name')
    procedure_definition_name = serializers.ReadOnlyField(source='procedure_definition.name')
    description = serializers.ReadOnlyField(source='test_sequence_definition.description')
    disposition_name = serializers.SerializerMethodField()
    customer_name = serializers.ReadOnlyField(source='work_order.project.customer.name')
    flash_start_datetime = serializers.SerializerMethodField()
    module_property= serializers.SerializerMethodField()
    correction_factor = serializers.SerializerMethodField()
    eg_number = serializers.IntegerField(source='linear_execution_group')
    is_updated = serializers.SerializerMethodField()
    old_correction_value = serializers.SerializerMethodField()
    date_time=serializers.SerializerMethodField()
    # bom=serializers.SerializerMethodField()

    asset_details = serializers.SerializerMethodField()
    calibrated_during_test= serializers.SerializerMethodField()

    def get_calibrated_during_test(self,obj):
        calibrated_during_test=StressRunResult.objects.filter(procedure_result_id=obj.id,stress_name='Test Start').first()
        if calibrated_during_test:
            return calibrated_during_test.is_calibrated
        else:
            return None
    
    def get_asset_details(self, obj):
        request = self.context.get('request')

        step_result = StepResult.objects.filter(
            procedure_result_id=obj.id
        ).first()

        if not step_result:
            return None

        measurement = MeasurementResult.objects.filter(
            step_result_id=step_result.id
        ).first()

        if not measurement:
            return None

        asset = AssetCalibration.objects.filter(
            asset_id=measurement.asset_id
        ).first()

        if not asset:
            return None

        serializer = AssetCalibrationSerializer(
            asset,
            context={'request': request}
        )

        return serializer.data

    def get_correction_factor(self, obj):
        # Get the first step result ID for the given procedure result
        stepresult_id = StepResult.objects.filter(procedure_result_id=obj.id).values_list('id', flat=True).first()
        # Fetch MeasurementResults with specific names
        measurementresults = MeasurementResult.objects.filter(step_result_id=stepresult_id,
                                                              name__in=["Imp", "Isc", "Vmp", "Voc", "Pmp"])
        correction_factor = {}
        # Iterate over the results and round the result_double values
        for measurementresult in measurementresults:
            if measurementresult.name is not None:
                # Check if result_double is not None before rounding
                if measurementresult.result_double is not None:
                    correction_factor[measurementresult.name] = round(measurementresult.result_double, 2)
                else:
                    correction_factor[measurementresult.name] = None  # Or set a default value if desired
        return correction_factor

    def get_flash_start_datetime(self, obj):
        # Filter StepResult by the specific ProcedureResult instance (obj)
        step_results = StepResult.objects.filter(
            procedure_result_id=obj
        )

        # Filter MeasurementResult by the related StepResult IDs and non-null start_datetime
        measurement_result = MeasurementResult.objects.filter(
            step_result_id__in=step_results,
            start_datetime__isnull=False
        ).first()

        if measurement_result:
            return measurement_result.start_datetime
        return None

    def get_disposition_name(self, obj):
        if obj.disposition:
            return obj.disposition.name
        else:
            return None

    def get_is_updated(self, obj):

        if MeasurementCorrectionFactor.objects.filter(old_procedure_result_id=obj.id).exists():
            return True
        else:
            return False

    def get_old_correction_value(self, obj):
        if MeasurementCorrectionFactor.objects.filter(old_procedure_result_id=obj.id).exists():
            measurement_results = MeasurementResult.objects.filter(step_result__procedure_result_id=obj.id)
            old_correction_values = []
            consolidated_result = {
                    "procedure_result_id": obj.id,
                    "step_result_id": None,  # You'll need to set this based on your context
                    "pmp": None,
                    "voc": None,
                    "vmp": None,
                    "isc": None,
                    "imp": None
                }

            # Create a mapping for specific names to be filtered
            target_names = ['Pmp', 'Voc', 'Vmp', 'Isc', 'Imp']

            # Loop through each measurement result
            for measurement_result in measurement_results:
                name = measurement_result.name
                value = measurement_result.result_double

                # Update the consolidated result dictionary based on the name
                if name == 'Pmp':
                    consolidated_result["pmp"] = round(value,2)
                elif name == 'Voc':
                    consolidated_result["voc"] = round(value,2)
                elif name == 'Vmp':
                    consolidated_result["vmp"] = round(value,2)
                elif name == 'Isc':
                    consolidated_result["isc"] = round(value,2)
                elif name == 'Imp':
                    consolidated_result["imp"] = round(value,2)

            # Assign the step_result_id if it's part of the measurement_result
            if measurement_results.exists():
                consolidated_result["step_result_id"] = measurement_results.first().step_result.id

            # Add the consolidated result to the old_correction_values
            old_correction_values = [consolidated_result]

            print(old_correction_values)
            return old_correction_values
    
    def get_date_time(self,obj):

        stepresult_id=StepResult.objects.filter(procedure_result_id=obj.id).values_list('id',flat=True).first()
        measurementresult_id=MeasurementResult.objects.filter(step_result_id=stepresult_id).values_list('date_time',flat=True).first()
        
        print(measurementresult_id)
        return measurementresult_id
    
    # def get_bom(obj,request):

    #     bom=WorkOrder.objects.filter(id=obj.work_order_id)
    #     return bom.name

    def get_module_property(self, obj):
        unit = Unit.objects.filter(id=obj.unit_id).first()
        if unit:
            unittype = unit.unit_type_id
            moduleproperty_id = UnitType.objects.filter(id=unittype).first()
            if moduleproperty_id:
                moduleproperty = moduleproperty_id.module_property_id
                var = ModuleProperty.objects.filter(id=moduleproperty).first()
                if var:
                    return {
                    "module_property_id":var.id,
                    "module_width": var.module_width,
                    "module_height": var.module_height,
                    "isc":var.isc,
                    "voc":var.voc,
                    "imp":var.imp,
                    "vmp":var.vmp,
                    "alpha_isc":var.alpha_isc,
                    "beta_voc":var.beta_voc
                }
        return None

    class Meta:
        model = ProcedureResult
        fields = [
            'id',
            'url',
            'name',
            'unit',
            'unit_serial_number',
            'procedure_definition',
            'procedure_definition_name',
            'disposition',
            'disposition_name',
            # 'bom',
            'start_datetime',
            'end_datetime',
            'project_number',
            'work_order',
            'work_order_name',
            'test_sequence_definition',
            'test_sequence_definition_name',
            'description',
            'customer_name',
            'flash_start_datetime',
            'correction_factor',
            'eg_number',
            'is_updated',
            'old_correction_value',
            'date_time',
            'module_property',
            'asset_details',
            'calibrated_during_test'
        ]
