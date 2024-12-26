from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken import views as rest_framework_views

from lsdb.views import ActionCompletionDefinitionViewSet
from lsdb.views import ActionDefinitionViewSet
from lsdb.views import ActionResultViewSet
from lsdb.views import ApiRequestLogViewSet
from lsdb.views import AssetCapacityViewSet
from lsdb.views import AssetTypeViewSet
from lsdb.views import AssetViewSet
from lsdb.views import AvailableDefectViewSet
from lsdb.views import AzureFileViewSet
from lsdb.views import ModulePropertyViewSet
from lsdb.views import ConditionDefinitionViewSet
from lsdb.views import CrateViewSet
from lsdb.views import CustomerViewSet
from lsdb.views import DispositionCodeViewSet
from lsdb.views import DispositionViewSet
from lsdb.views import ExpectedUnitTypeViewSet
from lsdb.views import FileFormatViewSet
from lsdb.views import ForgotPasswordViewSet
from lsdb.views import GroupTypeViewSet
from lsdb.views import GroupViewSet
from lsdb.views import LabelViewSet
from lsdb.views import LimitComparisonModeViewSet
from lsdb.views import LimitComparisonViewSet
from lsdb.views import LimitViewSet
from lsdb.views import LocationViewSet
from lsdb.views import ManageResultViewSet
from lsdb.views import MeasurementDefinitionViewSet
from lsdb.views import MeasurementResultTypeViewSet
from lsdb.views import MeasurementResultViewSet
from lsdb.views import MeasurementTypeViewSet
from lsdb.views import ModuleTechnologyViewSet
from lsdb.views import NoteViewSet
from lsdb.views import NoteTypeViewSet
from lsdb.views import NoopViewSet
from lsdb.views import OrganizationViewSet
# from lsdb.views import OutOfFamilyLimitViewSet
from lsdb.views import PermissionTypeViewSet
from lsdb.views import PermissionViewSet
from lsdb.views import PermittedViewViewSet
from lsdb.views import PluginViewSet
from lsdb.views import TestSequenceDefinitionViewSet
from lsdb.views import ProjectViewSet
from lsdb.views import PropertyViewSet
from lsdb.views import ProcedureDefinitionViewSet
from lsdb.views import ProcedureResultViewSet
from lsdb.views import SignInViewSet
from lsdb.views import SiPrefixViewSet
from lsdb.views import StepDefinitionViewSet
from lsdb.views import StepResultViewSet
from lsdb.views import StepTypeViewSet
from lsdb.views import TemplateViewSet
from lsdb.views import UnitTypeFamilyViewSet
from lsdb.views import UnitTypePropertyDataTypeViewSet
from lsdb.views import UnitTypePropertyResultViewSet
from lsdb.views import UnitTypePropertyTypeViewSet
from lsdb.views import UnitTypeViewSet
from lsdb.views import UnitViewSet
from lsdb.views import UserProfileViewSet
from lsdb.views import UserViewSet
from lsdb.views import UserRegistrationStatusViewSet
from lsdb.views import VisualizerViewSet
from lsdb.views import WorkOrderViewSet
from lsdb.views import GetNoteCountViewSet
from lsdb.views import UpdateProjectDetailsViewSet
from lsdb.views import ProjectModifiedDetailsViewSet
from lsdb.views import FailedProjectReportViewSet
from lsdb.views import verifyViewSet
from lsdb.views import CountViewSet
from lsdb.views import EngineeringAgendaViewSet
from lsdb.views import ActiveProjectsReportViewSet
from lsdb.views import DispositionBulkUpdateViewSet
from lsdb.views import ProjectDispositionViewSet
from lsdb.views import UpdateProjectforCustomerViewSet
from lsdb.views import NewCrateIntakeViewSet
from lsdb.views import CrateIntakeImagesViewSet
from lsdb.views import ModuleIntakeViewSet
from lsdb.views import GetModelTypeViewSet
from lsdb.views import GetModuleDetailsViewSet
from lsdb.views import ModuleIntakeDetailsViewSet
from lsdb.views import ModuleIntakeGridViewSet
from lsdb.views import CrateIntakeGridViewSet
from lsdb.views import ModuleIntakeImagesViewSet
from lsdb.views import ScannedPannelsViewSet
from lsdb.views import TestTypeViewSet
from lsdb.views import BulkInsertforScannedpanelsViewSet
from lsdb.views import GetAllCrateDetailsViewSet
from lsdb.views import GetAllModuleDetailsViewSet
from lsdb.views import ModuleInventoryViewSet
from lsdb.views import IntakeImagesInfoViewSet
from lsdb.views import IAMTestFileUploadViewSet
from lsdb.views import IAMTestViewSet
from lsdb.views import StepResultNotesViewSet
from lsdb.views import CrateUpdateViewSet
from lsdb.views import ModuleUpdateViewSet
from lsdb.views import FlashTestViewSet
from lsdb.views import ProcedureflagupdateViewSet
from lsdb.views import IVandEL_InProgressViewSet
from lsdb.views import LocationLogViewSet
from lsdb.views import MeasurementCorrectionFactorViewSet
from lsdb.views import FileUploadViewSet
from lsdb.views import FileUploadforFlashViewSet
from lsdb.views import FlashFileDownloadViewSet
from lsdb.views import ShippingFormViewSet
from lsdb.views import Customer_pichinaViewSet
from lsdb.views import UnitType_pichinaViewSet
from lsdb.views import ProjectDisposition_pichinaViewSet
from lsdb.views import Project_pichinaViewSet
from lsdb.views import Workorder_pichinaViewSet
from lsdb.views import Disposition_PichinaViewSet
from lsdb.views import ExpectedUnitType_pichinaViewSet
from lsdb.views import AuthUser_pichinaViewSet
from lsdb.views import Unit_pichinaViewSet
from lsdb.views import TestSequenceDefinition_pichinaViewSet
from lsdb.views import Location_pichinaViewSet
from lsdb.views import ManageResults_pichinaViewSet
from lsdb.views import Asset_pichinaViewSet
from lsdb.views import ModuleProperty_pichinaViewSet
from lsdb.views import ModuleTechnology_pichinaViewSet
from lsdb.views import MeasurementResult_pichinaViewSet
from lsdb.views import StepResult_pichinaViewSet
from lsdb.views import MeasurementDefinition_pichinaViewSet
from lsdb.views import StepType_pichinaViewSet
from lsdb.views import MeasurementType_pichinaViewSet
from lsdb.views import MeasurementResultType_pichinaViewSet
from lsdb.views import ProcedureResult_pichinaViewSet
from lsdb.views import StepDefinition_pichinaViewSet
from lsdb.views import ProcedureDefinition_pichinaViewSet
from lsdb.views import AzureFile_pichinaViewSet
from lsdb.views import AvailableDefect_pichinaViewSet
from lsdb.views import DeleteModuleIntakeIDViewSet
# from lsdb.views import ProcedureUpdateViewSet
# from lsdb.views import IAMMetaDataViewSet

router = DefaultRouter()
# router.register(r'action_completion_definitions', ApiRequestLogViewSet)
router.register(r'action_completion_definitions', ActionCompletionDefinitionViewSet)
router.register(r'action_definitions', ActionDefinitionViewSet)
router.register(r'action_results', ActionResultViewSet)
router.register(r'api_log', ApiRequestLogViewSet)
router.register(r'asset_capacities', AssetCapacityViewSet)
router.register(r'asset_types' , AssetTypeViewSet)
router.register(r'assets' , AssetViewSet)
router.register(r'available_defects' , AvailableDefectViewSet)
router.register(r'azure_files' , AzureFileViewSet)
router.register(r'module_properties' , ModulePropertyViewSet)
router.register(r'condition_definitions' , ConditionDefinitionViewSet)
router.register(r'crates' , CrateViewSet)
router.register(r'customers' , CustomerViewSet)
router.register(r'disposition_codes' , DispositionCodeViewSet)
router.register(r'dispositions' , DispositionViewSet)
router.register(r'expected_unit_types' , ExpectedUnitTypeViewSet)
router.register(r'file_formats', FileFormatViewSet)
router.register(r'forgot_password', ForgotPasswordViewSet)
router.register(r'group_types' , GroupTypeViewSet)
router.register(r'groups' , GroupViewSet)
router.register(r'labels' , LabelViewSet)
router.register(r'limit_comparison_modes' , LimitComparisonModeViewSet)
router.register(r'limit_comparisons' , LimitComparisonViewSet)
router.register(r'limits' , LimitViewSet)
router.register(r'locations', LocationViewSet)
router.register(r'manage_results',ManageResultViewSet, basename='manageresults')
router.register(r'measurement_definitions' , MeasurementDefinitionViewSet)
router.register(r'measurement_result_types' , MeasurementResultTypeViewSet)
router.register(r'measurement_results' , MeasurementResultViewSet)
router.register(r'measurement_types' , MeasurementTypeViewSet)
router.register(r'module_technologies' , ModuleTechnologyViewSet)
router.register(r'notes', NoteViewSet)
router.register(r'note_types', NoteTypeViewSet)
router.register(r'noop', NoopViewSet)
router.register(r'organizations' , OrganizationViewSet)
# router.register(r'out_of_family_limits', OutOfFamilyLimitViewSet)
router.register(r'plugins' , PluginViewSet)
router.register(r'permission_types' , PermissionTypeViewSet)
router.register(r'permissions' , PermissionViewSet)
router.register(r'permitted_views' , PermittedViewViewSet)
router.register(r'procedure_definitions' , ProcedureDefinitionViewSet)
router.register(r'procedure_results' , ProcedureResultViewSet)
router.register(r'projects' , ProjectViewSet)
router.register(r'properties' , PropertyViewSet)
router.register(r'si_prefixes' , SiPrefixViewSet)
router.register(r'signin', SignInViewSet)
router.register(r'step_definitions' , StepDefinitionViewSet)
router.register(r'step_results' , StepResultViewSet)
router.register(r'step_types' , StepTypeViewSet)
router.register(r'templates' , TemplateViewSet)
router.register(r'test_sequence_definitions' , TestSequenceDefinitionViewSet)
router.register(r'unit_type_families' , UnitTypeFamilyViewSet)
router.register(r'unit_type_property_data_types' , UnitTypePropertyDataTypeViewSet)
router.register(r'unit_type_property_results' , UnitTypePropertyResultViewSet)
router.register(r'unit_type_property_types' , UnitTypePropertyTypeViewSet)
router.register(r'unit_types' , UnitTypeViewSet)
router.register(r'units' , UnitViewSet)
router.register(r'user_profiles' , UserProfileViewSet)
router.register(r'users', UserViewSet)
router.register(r'user_registration_statuses' , UserRegistrationStatusViewSet)
router.register(r'visualizers' , VisualizerViewSet)
router.register(r'work_orders' , WorkOrderViewSet)
router.register(r'getnotecount',GetNoteCountViewSet, basename = 'getnotecount')
router.register(r'updateproject',UpdateProjectDetailsViewSet, basename = 'updateproject')
router.register(r'projectmodifieddetails',ProjectModifiedDetailsViewSet, basename= 'projectmodifieddetails')
router.register(r'failedprojectreport',FailedProjectReportViewSet, basename='failedprojectreport')
router.register(r'procedure_results_verify',verifyViewSet, basename = 'procedure_results_verify')
router.register(r'count',CountViewSet,basename='count')
router.register(r'engineeringagenda', EngineeringAgendaViewSet, basename='engineeringagenda')
router.register(r'activeprojectreport',ActiveProjectsReportViewSet, basename = 'activeprojectreport')
router.register(r'dispositionbulkupdate',DispositionBulkUpdateViewSet, basename = 'dispositionbulkupdate')
router.register(r'projectdisposition',ProjectDispositionViewSet, basename ='projectdisposition')
router.register(r'updateprojectforcustomer', UpdateProjectforCustomerViewSet, basename = 'updateprojectforcustomer')
router.register(r'new_crates', NewCrateIntakeViewSet, basename = 'new_crates')
router.register(r'crate_intake_images', CrateIntakeImagesViewSet, basename = 'crate_intake_images')
router.register(r'moduleintake', ModuleIntakeViewSet, basename = 'moduleintake')
router.register(r'getmodeltype', GetModelTypeViewSet, basename = 'getmodeltype')
router.register(r'getmoduledetails', GetModuleDetailsViewSet, basename = 'getmoduledetails')
router.register(r'moduleintakedetails', ModuleIntakeDetailsViewSet, basename = 'moduleintakedetails')
router.register(r'moduleintakegrid', ModuleIntakeGridViewSet, basename = 'moduleintakegrid')
router.register(r'crateintakegrid', CrateIntakeGridViewSet, basename = 'crateintakegrid')
router.register(r'module_intake_images', ModuleIntakeImagesViewSet, basename='module_intake_images')
router.register(r'scanned_pannels', ScannedPannelsViewSet, basename='scanned_pannels')
router.register(r'test-type', TestTypeViewSet, basename='test-type')
router.register(r'bulk_insert_for_scanned_panel',BulkInsertforScannedpanelsViewSet, basename='bulk_insert_for_scanned_panel')
router.register(r'get_all_module_details',GetAllModuleDetailsViewSet,basename = 'get_all_module_details')
router.register(r'get_all_crate_details',GetAllCrateDetailsViewSet,basename = 'get_all_crate_details')
router.register(r'module_inventory',ModuleInventoryViewSet,basename='module_inventory')
router.register(r'intake_images_info',IntakeImagesInfoViewSet, basename='intake_images_info')
router.register(r'IAMTest',IAMTestViewSet, basename = 'IAMTest')
router.register(r'IAMTestFileUpload',IAMTestFileUploadViewSet, basename = 'IAMTestFileUpload')
router.register(r'step_result_notes',StepResultNotesViewSet, basename='step_result_notes')
router.register(r'crate_update',CrateUpdateViewSet, basename='crate_update')
router.register(r'module_update',ModuleUpdateViewSet,basename='module_update')
router.register(r'flash_test',FlashTestViewSet,basename='flash_test')
router.register(r'procedureflagupdate',ProcedureflagupdateViewSet, basename = 'procedureflagupdate')
router.register(r'iv_el_inprogress',IVandEL_InProgressViewSet,basename = 'iv_el_inprogress')
router.register(r'location_log',LocationLogViewSet,basename='location_log')
router.register(r'measurement_correctionfactor',MeasurementCorrectionFactorViewSet,basename='measurement_correctionfactor')
router.register(r'upload',FileUploadViewSet,basename='upload')
router.register(r'flashupload',FileUploadforFlashViewSet,basename='flashupload')
router.register(r'downloadflashfile',FlashFileDownloadViewSet, basename = 'downloadflashfile')
router.register(r'shipping_form',ShippingFormViewSet,basename='shipping_form')
router.register(r'customer_pichina',Customer_pichinaViewSet, basename = 'customer_pichina')
router.register(r'unittype_pichina',UnitType_pichinaViewSet,basename='unittype_pichina')
router.register(r'disposition_pichina',ProjectDisposition_pichinaViewSet,basename = 'disposition_pichina')
router.register(r'project_pichina',Project_pichinaViewSet, basename = 'project_pichina')
router.register(r'disposition_Pichina',Disposition_PichinaViewSet,basename = 'disposition_Pichina')
router.register(r'workorder_pichina',Workorder_pichinaViewSet,basename = 'workorder_pichina')
router.register(r'expectedunittype_pichina',ExpectedUnitType_pichinaViewSet, basename = 'expectedunittype_pichina')
router.register(r'authuser_pichina',AuthUser_pichinaViewSet,basename = 'authuser_pichina')
router.register(r'unit_pichina',Unit_pichinaViewSet, basename = 'unit_pichina')
router.register(r'testsequencedefinition_pichina',TestSequenceDefinition_pichinaViewSet,basename= 'testsequencedefinition_pichina')
router.register(r'location_pichina',Location_pichinaViewSet, basename = 'location_pichina')
router.register(r'manage_results_pichina',ManageResults_pichinaViewSet,basename = 'manage_results_pichina')
router.register(r'asset_pichina',Asset_pichinaViewSet,basename = 'asset_pichina')
router.register(r'moduleproperty_pichina',ModuleProperty_pichinaViewSet, basename ='moduleproperty_pichina')
router.register(r'moduletechnology_pichina',ModuleTechnology_pichinaViewSet,basename = 'moduletechnology_pichina')
router.register(r'measurementresult_pichina',MeasurementResult_pichinaViewSet,basename = 'measurementresult_pichina')
router.register(r'stepresult_pichina',StepResult_pichinaViewSet,basename = 'stepresult_pichina')
router.register(r'measurementdefinition_pichina',MeasurementDefinition_pichinaViewSet,basename = 'measurementdefinition_pichina')
router.register(r'steptype_pichina',StepType_pichinaViewSet,basename = 'steptype_pichina')
router.register(r'measurementtype_pichina',MeasurementType_pichinaViewSet,basename = 'measurementtype_pichina')
router.register(r'measurementresulttype_pichina',MeasurementResultType_pichinaViewSet,basename = 'measurementresulttype_pichina')
router.register(r'procedureresult_pichina',ProcedureResult_pichinaViewSet,basename = 'procedureresult_pichina')
router.register(r'stepdefinition_pichina',StepDefinition_pichinaViewSet,basename = 'stepdefinition_pichina')
router.register(r'proceduredefinition_pichina',ProcedureDefinition_pichinaViewSet, basename = 'proceduredefinition_pichina')
router.register(r'azurefile_pichina',AzureFile_pichinaViewSet,basename = 'azurefile_pichina')
router.register(r'availabledefect_pichina',AvailableDefect_pichinaViewSet,basename = 'availabledefect_pichina')
router.register(r'deletemoduleintake',DeleteModuleIntakeIDViewSet,basename = 'deletemoduleintake')
# router.register(r'procupdate',ProcedureUpdateViewSet, basename = 'procupdate')
# router.register(r'IAMMetaData',IAMMetaDataViewSet, basename = 'IAMMetaData')


# app_name='lsdb'
urlpatterns =[
    # url(r'^admin/', include(admin.site.urls)),
    # url(r'^azure/', include('azure_ad_auth.urls')),
    # url(r'^login_successful/$', login_successful, name='login_successful'),
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls')),
]
