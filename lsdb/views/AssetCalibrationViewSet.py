from django.utils import timezone   
from rest_framework import viewsets
from lsdb.models import *
from lsdb.serializers import *
from django.db import connection
from rest_framework.response import Response
from rest_framework.decorators import action
from datetime import datetime
from django.core.mail import send_mail
from django.conf import settings


class AssetCalibrationViewSet(viewsets.ModelViewSet):
    logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
    queryset = AssetCalibration.objects.all().exclude(disposition_id=14)
    serializer_class = AssetCalibrationSerializer
    # pagination_class = None

    def patch(self, request, *args, **kwargs):
        asset_calibration_id = kwargs.get('pk')

        asset_calibration = AssetCalibration.objects.get(id=asset_calibration_id)
        asset = Asset.objects.get(id=asset_calibration.asset_id)

        asset.name = request.data.get('asset_name', asset.name)
        asset.description = request.data.get('description', asset.description)

        location_url = request.data.get('location')
        if location_url:
            location_id = location_url.rstrip('/').split('/')[-1]
            asset.location_id = location_id

        asset.save()

        asset_type_url = request.data.get('asset_type')
        if asset_type_url:
            asset_type_id = asset_type_url.rstrip('/').split('/')[-1]

            asset.asset_types.set([asset_type_id])

            
        return super().patch(request, *args, **kwargs)


    def partial_update(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        instance = self.get_object()
        notes = request.data.pop('notes', None)
        disposition_url = request.data.get('disposition')
        if disposition_url:
            disposition_id = disposition_url.rstrip('/').split('/')[-1]
        try:
            if 'disposition' in request.data:
                if AssetLastActionDetails.objects.filter(asset_id=pk).exists():
                    last_action = AssetLastActionDetails.objects.get(asset_id=pk)
                    last_action.action_name='Disposition Updated'
                    last_action.action_datetime=datetime.now()
                    last_action.user_id=request.user.id
                    last_action.save()
                    assetcalibration=AssetCalibration.objects.get(id=pk)
                    asset=Asset.objects.get(id=assetcalibration.asset_id)
                    asset.disposition_id=disposition_id
                    asset.save()
                else:
                    AssetLastActionDetails.objects.create(
                                                        asset_id=pk,
                                                        action_name='Disposition Updated',
                                                        action_datetime=datetime.now(),
                                                        user_id=request.user.id
                                                        )
                    assetcalibration=AssetCalibration.objects.get(id=pk)
                    asset=Asset.objects.get(id=assetcalibration.asset_id)
                    asset.disposition_id=disposition_id
                    asset.save()
            elif 'last_calibrated_date' in request.data:
                last_calibrated_date=request.data.pop('last_calibrated_date', None)
                requested_schedule_for_calibration=request.data.pop('requested_schedule_for_calibration')
                AssetLastActionDetails.objects.create(asset_id=pk,
                                                    action_name='Calibration Date Updated',
                                                    action_datetime=datetime.now(),
                                                    user_id=request.user.id,
                                                    notes=notes,
                                                    requested_last_calibrated_date=last_calibrated_date,
                                                    requested_schedule_for_calibration=requested_schedule_for_calibration
                                                    )
                try:
                    asset = AssetCalibration.objects.get(id=pk)
                    asset_name = asset.asset_name
                    user_email = request.user.email
                    subject = "Calibration Date Update Request"
                    message = f"""
                        Hi Team,

                        The calibration date for the asset has been updated and is awaiting approval.

                        Asset Name: {asset_name}
                        Requested Calibration Date: {last_calibrated_date}
                        Requested Schedule for Calibration: {requested_schedule_for_calibration} days
                        Updated By: {request.user.username}

                        Notes:
                        {notes}

                        This is an automated notification informing you that the calibration date has been changed and is pending approval.

                        Regards,
                        Asset Management System
                        """
                    send_mail(subject, message,settings.EMAIL_HOST_USER,[user_email, "sharumathi@gesain.net"],fail_silently=False)
                except Exception as e:
                    return Response({"Error": "Failed to send email.", "details": str(e)},status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            return super().partial_update(request, *args, **kwargs)
        except:
            return super().partial_update(request, *args, **kwargs)
            

    @action(detail=False, methods=['post'])
    def update_calibration_status(self, request):
        status=request.data.get('status')
        asset_id=request.data.get('asset_id')
        azure_file_id = None
        if 'azure_file' in request.data and request.data.get('azure_file'):
            azure_file_id = int(request.data.get('azure_file').rstrip('/').split('/')[-1])
        asset=AssetLastActionDetails.objects.filter(asset_id=asset_id,action_name='Calibration Date Updated').order_by('-id').first()
        asset.status=status
        asset.verified_by_id=request.user.id
        asset.azurefile_id = azure_file_id
        asset.save()
        if asset.status=="approved":
            AssetCalibration.objects.filter(id=asset_id).update(last_calibrated_date=asset.requested_last_calibrated_date,schedule_for_calibration=asset.requested_schedule_for_calibration,
                                                                is_calibration_required=True, azurefile_id = azure_file_id)
        try:
            if asset.status=="approved":
                asset_obj = AssetCalibration.objects.get(id=asset_id)
                schedule_days = f"{asset.requested_schedule_for_calibration} days"
                subject = "Calibration Request Verified"
                message = f"""
                    Hi Team,

                    The calibration request for the asset has been verified.

                    Asset Name: {asset_obj.asset_name}
                    Requested Calibration Date: {asset.requested_last_calibrated_date}
                    Requested Schedule for Calibration: {schedule_days}

                    Notes:
                    {asset.notes}

                    Verified By: {request.user.username}
                    Status: {asset.status}

                    This is to inform you that the calibration request has been reviewed and verified.
                    """
                send_mail(subject,message,settings.EMAIL_HOST_USER,[request.user.email,  "sharumathi@gesain.net"],fail_silently=False)
            elif asset.status=="reject":
                asset_obj = AssetCalibration.objects.get(id=asset_id)
                schedule_days = f"{asset.requested_schedule_for_calibration} days"
                subject = "Calibration Request Rejected"
                message = f"""
                    Hi Team,

                    The calibration request for the asset has been rejected.

                    Asset Name: {asset_obj.asset_name}
                    Requested Calibration Date: {asset.requested_last_calibrated_date}
                    Requested Schedule for Calibration: {schedule_days}

                    Notes:
                    {asset.notes}

                    Verified By: {request.user.username}
                    Status: {asset.status}

                    This is to inform you that the calibration request has been reviewed and rejected.
                    """
                send_mail(subject,message,settings.EMAIL_HOST_USER,[request.user.email,  "sharumathi@gesain.net"],fail_silently=False)
        except Exception as e:
            return Response({"Error": "Failed to send verification email", "details": str(e)},status=500)
        return Response ({"detail":"Asset status updated"},status=200)

        
    @action(detail=False, methods=['get'])
    def calibration_history(self, request):
        asset_id = request.query_params.get('asset_id', None)
        asset_instance = AssetCalibration.objects.filter(id=asset_id).first()
        history = AssetLastActionDetails.objects.filter(
            asset_id=asset_id,
            action_name='Calibration Date Updated'
        ).order_by('-action_datetime')
        results = []
        for item in history:
            if item.status=='reject':
                calibration_date=item.requested_last_calibrated_date
            elif item.status=='approved':
                calibration_date=asset_instance.last_calibrated_date
            else:
                calibration_date=None
            results.append({
                "calibration_date": calibration_date if asset_instance else None,
                "note": item.notes if item.notes else None,
                "calibrated_by": item.user.username if item.user else None,
                "verified_by": item.verified_by.username if item.verified_by else None,
                "status": item.status if item.status else None,
                "updated_on": item.action_datetime if item.action_datetime else None,
                "file": "https://lsdbhaveblueuat.azurewebsites.net/api/1.0/azure_files/"+str(item.azurefile_id)+"/download" if item.azurefile_id else None
            })

        return Response(results)


    def perform_create(self, serializer):
        if self.request.method == 'POST':
            is_main_asset_str = self.request.data.get('is_main_asset')
            asset_type_id = self.request.data.get('asset_type')
            is_main_asset = str(is_main_asset_str).lower() == 'true'
            asset_calibration = None
            if is_main_asset:
                asset_calibration = serializer.save(
                    is_sub_asset=False, is_rack=False, disposition_id=16
                )
            elif not is_main_asset and asset_type_id in [66]:
                asset_calibration = serializer.save(
                    is_sub_asset=False, is_rack=True, disposition_id=16
                )
            elif is_main_asset is False:
                asset_calibration = serializer.save(
                    is_sub_asset=True, is_rack=False, disposition_id=16
                )
            if not asset_calibration:
                raise ValueError("Could not create AssetCalibration: invalid is_main_asset or asset_type")
            asset = Asset.objects.create(
                name=asset_calibration.asset_name,
                description=asset_calibration.description,
                location_id=asset_calibration.location.id,
                last_action_datetime=asset_calibration.last_action_datetime,
                disposition_id=16
            )
            asset_calibration.asset = asset
            asset_calibration.save(update_fields=['asset'])
            if asset_calibration.asset_type:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """
                        INSERT INTO lsdb_asset_asset_types (asset_id, assettype_id)
                        VALUES (%s, %s)
                        """,
                        [asset.id, asset_calibration.asset_type.id]
                    )


    @action(detail=False, methods=['post','get'])         
    def psr_subassets(self,request):
        if self.request.method=='GET':
            psr_subassets=AssetCalibration.objects.filter(is_main_asset=False,is_sub_asset=True,is_rack=False,asset_type_id=23)
            serializer = self.get_serializer(psr_subassets, many=True)
            data = serializer.data
            filtered_data = [{k: d[k] for k in ("id", "asset_name", "asset_number","asset_type","asset_type_name","disposition_id","is_calibration_date","asset_next_calibration","in_use","is_calibration")} for d in data]            
            return Response(filtered_data, status=200)
        
        elif self.request.method=='POST':
            asset_calibration_id=self.request.data.get('asset_calibration_id')
            sub_asset_ids=self.request.data.get('sub_asset_ids')
            for sub_asset_id in sub_asset_ids:
                AssetSubAsset.objects.create(asset_id=asset_calibration_id,sub_asset_id=sub_asset_id,linked_date=timezone.now())
            return Response ({"detail":"Asset Linked"},status=200)


    @action(detail=False, methods=['post','get','put','delete'])
    def link_asset_subasset(self,request):
        if self.request.method=='GET':
            is_main_asset = request.query_params.get('is_main_asset')
            if is_main_asset is None:
                return Response({"error": "is_main_asset parameter is required"}, status=400)
            if isinstance(is_main_asset, str):
                is_main_asset = is_main_asset.lower() in ['true', '1', 'yes']
            assets = AssetCalibration.objects.filter(is_main_asset=is_main_asset)
            serializer = self.get_serializer(assets, many=True) 
            return Response(serializer.data, status=200)
            
        elif self.request.method=='POST':
            asset_calibration_id=self.request.data.get('asset_calibration_id')
            sub_asset_ids=self.request.data.get('sub_asset_ids')

            for sub_asset_id in sub_asset_ids:
                AssetSubAsset.objects.create(asset_id=asset_calibration_id,sub_asset_id=sub_asset_id,linked_date=timezone.now())
            return Response ({"detail":"Asset Linked"},status=200)
        
        elif self.request.method=='PUT':
            asset_calibration_id=request.data.get('asset_calibration_id')
            sub_asset_ids=request.data.get('sub_asset_ids')
            AssetSubAsset.objects.filter(asset_id=asset_calibration_id).delete()
            for sub_asset_id in sub_asset_ids:
                AssetSubAsset.objects.create(asset_id=asset_calibration_id,sub_asset_id=sub_asset_id,linked_date=timezone.now())
            return Response ({"detail":"Asset Re-Linked"},status=200)
        
        elif self.request.method=='DELETE':
            asset_calibration_id= request.query_params.get('asset_calibration_id')
            AssetSubAsset.objects.filter(asset_id=asset_calibration_id).delete()
            return Response ({"detail":"Asset Unlinked"},status=200)

    @action(detail=False, methods=['get'])
    def edit_asset_get(self, request):
        asset_calibration_id = request.query_params.get('id')
        if not asset_calibration_id:
            return Response({"error": "Asset Calibration ID is required"}, status=400)
        try:
            asset_calibrations = AssetCalibration.objects.filter(is_sub_asset=True)
            linked_subassets = AssetSubAsset.objects.filter(asset_id=asset_calibration_id)
            linked_subasset_ids = {subasset.sub_asset.id for subasset in linked_subassets}
            serializer = self.get_serializer(asset_calibrations, many=True)
            serialized_data = serializer.data
            output = []
            for asset in serialized_data:
                asset_id = asset.get("id")
                is_linked = asset_id in linked_subasset_ids
                asset["is_linked"] = is_linked
                output.append(asset)
            return Response(output, status=200)
        except AssetCalibration.DoesNotExist:
            return Response({"error": "Asset Calibration not found"}, status=404)
        

    @action(detail=False, methods=['get'])
    def asset_info(self, request):
        asset_id = request.query_params.get('asset_id')
        if not asset_id:
            return Response({"error": "Asset ID is required"}, status=400)
        try:
            asset_calibration = AssetCalibration.objects.get(asset_id=asset_id)
            serializer = self.get_serializer(asset_calibration)
            data = serializer.data
            return Response({
                "last_calibrated_date": data["last_calibrated_date"],
                "next_calibration_date": data["next_calibration_date"],
                "asset_name": data["asset_name"],
                "calibration_days": data["calibration_days"],
                "is_calibration": data["is_calibration"],
                "days_to_next_calibration": data["asset_next_calibration"]
            }, status=200)
        except AssetCalibration.DoesNotExist:
            asset=Asset.objects.get(id=asset_id)
            AssetCalibration.objects.create(asset_id=asset.id,asset_number=asset.name,asset_name=asset.name,last_action_datetime=asset.last_action_datetime,
                                            location_id=asset.location_id,is_calibration_required=False,schedule_for_calibration=0,external_asset_required=False,
                                            is_main_asset=True,is_sub_asset=False,is_rack=False,disposition_id=16,last_calibrated_date=None)
            asset_calibration = AssetCalibration.objects.get(asset_id=asset_id)
            serializer = self.get_serializer(asset_calibration)
            data = serializer.data
            return Response({
                "last_calibrated_date": data["last_calibrated_date"],
                "next_calibration_date": data["next_calibration_date"],
                "asset_name": data["asset_name"],
                "calibration_days": data["calibration_days"],
                "is_calibration": data["is_calibration"],
                "days_to_next_calibration": data["asset_next_calibration"]
            }, status=200)
            
        
    @action(detail=False, methods=['get', ],
            serializer_class=DispositionCodeListSerializer)
    def asset_dispositions(self, request, pk=None):
        self.context = {'request': request}
        serializer = DispositionCodeListSerializer(DispositionCode.objects.get(name='asset_management'),many=False,context={'request': request})
        return Response(serializer.data)
    

    # @action(detail=False, methods=['get'])
    # def asset_list(self, request):
    #     is_main_asset = request.query_params.get('is_main_asset')
    #     if is_main_asset is None:
    #         return Response({"error": "is_main_asset parameter is required"}, status=400)
    #     assets = AssetCalibration.objects.filter(is_main_asset=is_main_asset)
    #     serializer = self.get_serializer(assets, many=True) 
    #     return Response(serializer.data, status=200)

    @action(detail=False, methods=['post','get'])         
    def search(self,request):
        if self.request.method=='GET':
            asset_number=request.query_params.get('asset_number')
            filters={}

            if asset_number:
                filters['asset_number__icontains']=asset_number

            assets=AssetCalibration.objects.filter(**filters)
            
            page = self.paginate_queryset(assets)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)
    
            serializer = self.get_serializer(assets, many=True)
            return Response(serializer.data, status=200)