import graphene
from lsdb.schema import Query as LsdbQuery
from lsdb.schema import NotesFlagPageType
from lsdb.schema import ModuleIntakePageType,ModuleIntakeGridPagesType,CustomerPageType, CrateIntakePaginationType

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
module_intake_grid_schema = graphene.Schema(query=ModuleIntakeGridOnlyQuery)


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
module_intake_schema = graphene.Schema(query=ModuleIntakeOnlyQuery)


# crete Intake get customers
class CustomerOnlyQuery(graphene.ObjectType):
    customers = graphene.Field(
    CustomerPageType,
    limit=graphene.Int(),
    offset=graphene.Int(),
    )
    def resolve_customers(self, info):
        return LsdbQuery.resolve_customers(self, info)
customer_schema = graphene.Schema(query=CustomerOnlyQuery)


# Crate Intake get
class CrateIntakeOnlyQuery(graphene.ObjectType):
    crate_intakes = graphene.Field(
        CrateIntakePaginationType,
        limit=graphene.Int(),
        offset=graphene.Int(),
    )
    def resolve_crate_intakes(self, info, limit=100, offset=0):
        return LsdbQuery.resolve_crate_intakes(self, info, limit=limit, offset=offset)
crate_schema = graphene.Schema(query=CrateIntakeOnlyQuery)