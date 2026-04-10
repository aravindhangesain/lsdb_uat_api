import graphene
from lsdb.schema import Query as LsdbQuery
from lsdb.schema import NotesFlagPageType
from lsdb.schema import (ModuleIntakePageType,ModuleIntakeGridPagesType,CustomerPageType, 
                         CrateIntakePaginationType,ActiveProjectGridPagesType,AssignUnitsResponseType,
                         WorkOrderListResponse)

# Initial
class Query(LsdbQuery, graphene.ObjectType):
    pass
schema = graphene.Schema(query=Query)


# Only for flags
class FlagsOnlyQuery(graphene.ObjectType):
    flags = graphene.Field(
        NotesFlagPageType,
        limit=graphene.Int(),
        offset=graphene.Int(),
    )
    def resolve_flags(self, info, limit=100, offset=0):
        return LsdbQuery.resolve_flags(self, info, limit=limit, offset=offset)
flags_schema = graphene.Schema(query=FlagsOnlyQuery)


# Only for Module Intake Details
class ModuleIntakeGridOnlyQuery(graphene.ObjectType):
    details = graphene.Field(
        ModuleIntakeGridPagesType,
        limit=graphene.Int(),
        offset=graphene.Int(),
    )
    def resolve_details(self, info, limit=None, offset=0):
        return LsdbQuery.resolve_details(
            self,
            info,
            limit=limit,
            offset=offset
        )
module_intake_grid_schema = graphene.Schema(query=ModuleIntakeGridOnlyQuery, auto_camelcase=False)


# MODULE INTAKE ONLY 
class ModuleIntakeOnlyQuery(graphene.ObjectType):
    module_intake_details = graphene.Field(
        ModuleIntakePageType,
        limit=graphene.Int(),
        offset=graphene.Int(),
    )
    def resolve_module_intake_details(self, info, limit=100, offset=0):
        return LsdbQuery.resolve_module_intake_details(
            self, info, limit=limit, offset=offset
        )
module_intake_schema = graphene.Schema(query=ModuleIntakeOnlyQuery, auto_camelcase=False)


# crete Intake get customers
class CustomerOnlyQuery(graphene.ObjectType):
    customers = graphene.Field(
    CustomerPageType,
    limit=graphene.Int(),
    offset=graphene.Int(),
    )
    def resolve_customers(self, info):
        return LsdbQuery.resolve_customers(self, info)
customer_schema = graphene.Schema(query=CustomerOnlyQuery, auto_camelcase=False)


# Crate Intake get
class CrateIntakeOnlyQuery(graphene.ObjectType):
    crate_intakes = graphene.Field(
        CrateIntakePaginationType,
        limit=graphene.Int(),
        offset=graphene.Int(),
    )
    def resolve_crate_intakes(self, info, limit=100, offset=0):
        return LsdbQuery.resolve_crate_intakes(self, info, limit=limit, offset=offset)
crate_schema = graphene.Schema(query=CrateIntakeOnlyQuery, auto_camelcase=False)


#Active Projects Only Query
class ActiveProjectsOnlyQuery(graphene.ObjectType):
    active_projects = graphene.Field(
        ActiveProjectGridPagesType,
        show_archived=graphene.Boolean(),
        location=graphene.Int(),
        limit=graphene.Int(),
        offset=graphene.Int()
    )
    def resolve_active_projects(self, info, show_archived=True, location=None, limit=100, offset=0):
        return LsdbQuery.resolve_active_projects(self,info,show_archived=show_archived,location=location,limit=limit,offset=offset)
active_projects_schema = graphene.Schema(query=ActiveProjectsOnlyQuery,auto_camelcase=False)


#Active Project Assign_units Only Query
class AssignUnitsOnlyQuery(graphene.ObjectType):
    assign_units = graphene.Field(
        AssignUnitsResponseType,
        work_order_id=graphene.Int(required=True),
    )
    def resolve_assign_units(self, info, work_order_id):
        return LsdbQuery.resolve_assign_units(self,info,work_order_id=work_order_id)
assign_units_schema = graphene.Schema(query=AssignUnitsOnlyQuery,auto_camelcase=False)

# Active project work order 
class WorkOrderOnlyQuery(graphene.ObjectType):
    work_order = graphene.Field(
        WorkOrderListResponse,
        project_id=graphene.Int(required=True),
    )
    def resolve_work_order(self, info,project_id):
        return LsdbQuery.resolve_work_order(self, info,project_id=project_id)
work_order_schema = graphene.Schema(query=WorkOrderOnlyQuery, auto_camelcase=False)