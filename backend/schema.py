import graphene
from lsdb.schema import Query as LsdbQuery
from lsdb.schema import NotesPageType

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