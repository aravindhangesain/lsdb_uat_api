import graphene
from lsdb.schema import Query as LsdbQuery
from lsdb.schema import NotesPageType
from lsdb.schema import ModuleIntakePageType,ModuleIntakeGridPagesType
# Initial

class Query(LsdbQuery, graphene.ObjectType):
    pass
schema = graphene.Schema(query=Query)


# Only for flags

class FlagsOnlyQuery(graphene.ObjectType):
    flags = graphene.Field(
        NotesPageType,
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