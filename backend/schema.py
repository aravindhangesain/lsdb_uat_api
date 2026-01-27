# backend/schema.py
import graphene
from lsdb.schema import Query as LsdbQuery  # we’ll create this next

class Query(LsdbQuery, graphene.ObjectType):
    pass

schema = graphene.Schema(query=Query)
