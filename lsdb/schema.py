import graphene
from graphene_django import DjangoObjectType
from django.db.models import Max, Exists, OuterRef
from django.contrib.auth import get_user_model
from graphql import GraphQLError
from numpy import info

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


class NoteType(DjangoObjectType):
    # ---- Computed / renamed fields ----
    owner_name = graphene.String()
    username = graphene.String()
    note_type_name = graphene.String()
    disposition_name = graphene.String()
    disposition_complete = graphene.Boolean()
    read = graphene.Boolean()
    last_update_datetime = graphene.DateTime()

    # ---- Nested / custom ----
    attachments = graphene.List(AzureFileType)
    labels = graphene.List(LabelType)
    tagged_users = graphene.List(UserType)
    parent_objects = graphene.List(ParentObjectType)

    class Meta:
        model = Note
        fields = "__all__"


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
        date_time = (
            Note.objects
            .filter(parent_note=self)
            .aggregate(Max("datetime"))
            .get("datetime__max")
        )
        return date_time or self.datetime

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
                parents = rel.remote_field.model.objects.filter(
                    notes__in=[self.id]
                )

                for parent in parents:
                    parent_objects.append({
                        "model_name": parent._meta.model_name,
                        "id": parent.id,
                        "str": str(parent.__str__()),
                    })

        return parent_objects
    

class NotesPageType(graphene.ObjectType):
    items = graphene.List(NoteType)
    total_count = graphene.Int()
    has_next = graphene.Boolean()

class Query(graphene.ObjectType):
    notes = graphene.Field(
        NotesPageType,
        note_type=graphene.String(required=True),
        completed=graphene.Boolean(),
        limit=graphene.Int(),
        offset=graphene.Int(),
    )

    def resolve_notes(self,info,note_type,completed=False,limit=20,offset=0,):
        user = info.context.user
        if not user.is_authenticated:
            raise GraphQLError("Authentication required")

        qs = Note.objects.filter(
            note_type__name=note_type,
            disposition__complete=completed
        )
        read_subquery = NoteReadStatus.objects.filter(
            note=OuterRef("pk"),
            user=user
        )
        qs = (
            qs.annotate(read=Exists(read_subquery))
            .select_related(
                "user",
                "owner",
                "note_type",
                "disposition",
            )
            .prefetch_related(
                "labels",
                "attachments",
                "tagged_users",
            )
            .distinct()
        )
        total_count = qs.count()
        if limit == -1:
            items = qs
            has_next = False
        else:
            items = qs[offset : offset + limit]
            has_next = offset + limit < total_count

        return NotesPageType(
            items=items,
            total_count=total_count,
            has_next=has_next,
        )

