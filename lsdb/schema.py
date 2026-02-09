import graphene
from graphene_django import DjangoObjectType
from django.db.models import Max, Exists, OuterRef
from django.contrib.auth import get_user_model
from graphql import GraphQLError
from numpy import info
import graphene
from graphene_django import DjangoObjectType
from django.db.models import Max, Exists, OuterRef, Q
from django.contrib.auth import get_user_model
from graphql import GraphQLError
from functools import reduce
from operator import or_
from django.db.models import Q

from lsdb.models import (
    Note,
    AzureFile,
    Label,
    NoteReadStatus,
)

from lsdb.models import (
    Note,
    AzureFile,
    Label,
    NoteReadStatus,
)

User = get_user_model()

class UserType(DjangoObjectType):
    class Meta:
        model = User
        fields = ("id", "username")


class AzureFileType(DjangoObjectType):
    class Meta:
        model = AzureFile
        fields = "__all__"


class LabelType(DjangoObjectType):
    class Meta:
        model = Label
        fields = "__all__"

class ParentObjectType(graphene.ObjectType):
    model_name = graphene.String()
    id = graphene.Int()
    str = graphene.String()


# class NoteType(DjangoObjectType):
#     # ---- Computed / renamed fields ----
#     owner_name = graphene.String()
#     username = graphene.String()
#     note_type_name = graphene.String()
#     disposition_name = graphene.String()
#     disposition_complete = graphene.Boolean()
#     read = graphene.Boolean()
#     last_update_datetime = graphene.DateTime()

#     # ---- Nested / custom ----
#     attachments = graphene.List(AzureFileType)
#     labels = graphene.List(LabelType)
#     tagged_users = graphene.List(UserType)
#     parent_objects = graphene.List(ParentObjectType)

#     class Meta:
#         model = Note
#         fields = "__all__"


#     def resolve_owner_name(self, info):
#         return self.owner.username if self.owner else None

#     def resolve_username(self, info):
#         return self.user.username if self.user else None

#     def resolve_note_type_name(self, info):
#         return self.note_type.name if self.note_type else None

#     def resolve_disposition_name(self, info):
#         return self.disposition.name if self.disposition else None

#     def resolve_disposition_complete(self, info):
#         return self.disposition.complete if self.disposition else None

#     def resolve_read(self, info):
#         return getattr(self, "read", False)

#     def resolve_last_update_datetime(self, info):
#         date_time = (
#             Note.objects
#             .filter(parent_note=self)
#             .aggregate(Max("datetime"))
#             .get("datetime__max")
#         )
#         return date_time or self.datetime

#     def resolve_attachments(self, info):
#         return self.attachments.all()

#     def resolve_labels(self, info):
#         return self.labels.all()

#     def resolve_tagged_users(self, info):
#         return self.tagged_users.all()

#     def resolve_parent_objects(self, info):
#         parent_objects = []
#         related_objects = self._meta.related_objects

#         for rel in related_objects:
#             if rel.remote_field.name == "notes":
#                 parents = rel.remote_field.model.objects.filter(
#                     notes__in=[self.id]
#                 )

#                 for parent in parents:
#                     parent_objects.append({
#                         "model_name": parent._meta.model_name,
#                         "id": parent.id,
#                         "str": str(parent.__str__()),
#                     })

#         return parent_objects
    

# class NotesPageType(graphene.ObjectType):
#     items = graphene.List(NoteType)
#     total_count = graphene.Int()
#     has_next = graphene.Boolean()

# class Query(graphene.ObjectType):
#     notes = graphene.Field(
#         NotesPageType,
#         note_type=graphene.String(required=True),
#         completed=graphene.Boolean(),
#         limit=graphene.Int(),
#         offset=graphene.Int(),
#     )

#     def resolve_notes(self,info,note_type,completed=False,limit=20,offset=0,):
#         user = info.context.user
#         if not user.is_authenticated:
#             raise GraphQLError("Authentication required")

#         qs = Note.objects.filter(
#             note_type__name=note_type,
#             disposition__complete=completed
#         )
#         read_subquery = NoteReadStatus.objects.filter(
#             note=OuterRef("pk"),
#             user=user
#         )
#         qs = (
#             qs.annotate(read=Exists(read_subquery))
#             .select_related(
#                 "user",
#                 "owner",
#                 "note_type",
#                 "disposition",
#             )
#             .prefetch_related(
#                 "labels",
#                 "attachments",
#                 "tagged_users",
#             )
#             .distinct()
#         )
#         total_count = qs.count()
#         if limit == -1:
#             items = qs
#             has_next = False
#         else:
#             items = qs[offset : offset + limit]
#             has_next = offset + limit < total_count

#         return NotesPageType(
#             items=items,
#             total_count=total_count,
#             has_next=has_next,
#         )

User = get_user_model()


# =====================================================
# Types
# =====================================================

class UserType(DjangoObjectType):
    class Meta:
        model = User
        fields = ("id", "username")


class AzureFileType(DjangoObjectType):
    class Meta:
        model = AzureFile
        fields = "__all__"


class LabelType(DjangoObjectType):
    class Meta:
        model = Label
        fields = "__all__"


class ParentObjectType(graphene.ObjectType):
    model_name = graphene.String()
    id = graphene.Int()
    str = graphene.String()


# =====================================================
# Note Type
# =====================================================

class NoteType(DjangoObjectType):
    owner_name = graphene.String()
    username = graphene.String()
    note_type_name = graphene.String()
    disposition_name = graphene.String()
    disposition_complete = graphene.Boolean()
    read = graphene.Boolean()
    last_update_datetime = graphene.DateTime()


    attachments = graphene.List(AzureFileType)
    labels = graphene.List(LabelType)
    tagged_users = graphene.List(UserType)
    parent_objects = graphene.List(ParentObjectType)
    project=graphene.List(graphene.Int)
    class Meta:
        model = Note
        fields = "__all__"

    # -------------------------
    # Computed fields
    # -------------------------

    def resolve_owner_name(self, info):
        return self.owner.username if self.owner else None

    def resolve_username(self, info):
        return self.user.username if self.user else None

    def resolve_note_type_name(self, info):
        return self.note_type.name if self.note_type else None

    def resolve_disposition_name(self, info):
        return self.disposition.name if self.disposition else None

    def resolve_disposition_complete(self, info):
        return self.disposition.complete if self.disposition else None

    def resolve_read(self, info):
        return getattr(self, "read", False)

    def resolve_last_update_datetime(self, info):
        dt = (
            Note.objects
            .filter(parent_note=self)
            .aggregate(Max("datetime"))
            .get("datetime__max")
        )
        return dt or self.datetime

    # -------------------------
    # relations
    # -------------------------

    def resolve_attachments(self, info):
        return self.attachments.all()

    def resolve_labels(self, info):
        return self.labels.all()

    def resolve_tagged_users(self, info):
        return self.tagged_users.all()

    def resolve_parent_objects(self, info):
        parent_objects = []
        related_objects = self._meta.related_objects

        for rel in related_objects:
            if rel.remote_field.name == "notes":
                parents = rel.remote_field.model.objects.filter(notes__in=[self.id])

                for parent in parents:
                    parent_objects.append(
                        ParentObjectType(
                            model_name=parent._meta.model_name,
                            id=parent.id,
                            str=str(parent)
                        )
                    )

        return parent_objects
    
    def resolve_project(self,info):
        return self.project_set.values_list("id", flat=True)
    
    



# =====================================================
# Pagination Type
# =====================================================

class NotesPageType(graphene.ObjectType):
    items = graphene.List(NoteType)
    total_count = graphene.Int()
    has_next = graphene.Boolean()


# =====================================================
# Filter Input  ⭐ (NEW)
# =====================================================

class NoteFilterInput(graphene.InputObjectType):
    id=graphene.Int()
    note_type = graphene.List(graphene.String)
    subject = graphene.List(graphene.String)
    owner = graphene.List(graphene.String)
    author = graphene.List(graphene.String)
    tagged_users=graphene.List(graphene.String)
    labels = graphene.List(graphene.String)
    status = graphene.List(graphene.String)
    start_date = graphene.Date()
    end_date = graphene.Date()
    creation_date = graphene.Date()
    search = graphene.String()   # global search
    order_by = graphene.String() # sorting
    project_id = graphene.List(graphene.Int)
# =====================================================
# Query
# =====================================================
class Query(graphene.ObjectType):
    notes = graphene.Field(
        NotesPageType,
        filters=NoteFilterInput(),
        limit=graphene.Int(),
        offset=graphene.Int(),
    )

    # -------------------------------------------------
    # Resolver
    # -------------------------------------------------

    def resolve_notes(self, info, filters=None, limit=20, offset=0):
        user = info.context.user

        if not user.is_authenticated:
            user = User.objects.first()
            # raise GraphQLError("Authentication required")

        qs = Note.objects.all()

        q = Q()

        # =============================
        # Dynamic Filters
        # =============================

        if filters:
            if filters.id:
                q &= Q(id=filters.id)

            if filters.note_type:
                q &= reduce(or_,
                (Q(note_type__name__icontains=v) for v in filters.note_type))

            if filters.subject:
                q &= reduce(or_,
                (Q(subject__icontains=v) for v in filters.subject))

            if filters.owner:
                q &= reduce(or_,
                (Q(owner__username__icontains=v) for v in filters.owner))

            if filters.author:
                q &= reduce(or_,
                (Q(user__username__icontains=v) for v in filters.author))
            
            if filters.tagged_users:
                q &= reduce(or_,
                (Q(tagged_users__username__icontains=v) for v in filters.tagged_users))


            if filters.status:
                bool_values = []

                for v in filters.status:
                    if isinstance(v, bool):
                        bool_values.append(v)
                    elif isinstance(v, str):
                        if v.lower() == "true":
                            bool_values.append(True)
                        elif v.lower() == "false":
                            bool_values.append(False)

                if bool_values:
                    q &= Q(disposition__complete__in=bool_values)

            if filters.labels:
                q &= Q(labels__name__in=filters.labels)

            if filters.start_date:
                q &= Q(datetime__date__gte=filters.start_date)

            if filters.end_date:
                q &= Q(datetime__date__lte=filters.end_date)
            
            if filters.creation_date:
                q &= Q(datetime__date=filters.creation_date)
            
            if filters.project_id:
                q &= Q(project__id__in=filters.project_id)

            if filters.search:
                q &= (
                    Q(subject__icontains=filters.search) |
                    Q(description__icontains=filters.search)
                )

        qs = qs.filter(q)

        # =============================
        # Read annotation
        # =============================

        read_subquery = NoteReadStatus.objects.filter(
            note=OuterRef("pk"),
            user=user
        )

        qs = (
            qs.annotate(read=Exists(read_subquery))
            .select_related("user", "owner", "note_type", "disposition")
            .prefetch_related("labels", "attachments", "tagged_users","project_set")
            .distinct()
        )

        # =============================
        # Sorting
        # =============================

        if filters and filters.order_by:
            qs = qs.order_by(filters.order_by)

        # =============================
        # Pagination
        # =============================

        total_count = qs.count()

        if limit == -1:
            items = qs
            has_next = False
        else:
            items = qs[offset: offset + limit]
            has_next = offset + limit < total_count

        return NotesPageType(
            items=items,
            total_count=total_count,
            has_next=has_next,
        )
