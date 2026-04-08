import json
import graphene
from operator import or_
from functools import reduce
from django.db import connection
from graphene_django import DjangoObjectType
from django.contrib.auth import get_user_model
from graphene.types.generic import GenericScalar
from django.db.models import Max, Exists, OuterRef, Q
from django.core.serializers.json import DjangoJSONEncoder


from lsdb.models import (
    Note,
    AzureFile,
    Label,
    NoteReadStatus,
    ProcedureResult,
    Unit,
    MeasurementResult,
    Customer, 
    LocationLog, 
    Location, 
    WorkOrder, 
    NewCrateIntake,
    ModuleIntakeDetails
)


from lsdb.serializers.ProcedureResultSerializer import (
    FailedProjectReportSerializer,
    MssFailedProjectReportSerializer
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

# ============================================
# MODULE INTAKE TYPES (NEW)
# ============================================

class ProjectType(graphene.ObjectType):
    project_id = graphene.Int()
    project_number = graphene.String()

class CustomerType(graphene.ObjectType):
    customer_id = graphene.Int()
    customer_name = graphene.String()

class LocationType(graphene.ObjectType):
    location_id = graphene.Int()
    location_name = graphene.String()

class CrateType(graphene.ObjectType):
    id = graphene.Int()
    crate_name = graphene.String()

# =====================================================
# ModuleIntakeGrid Type
# =====================================================

class ModuleIntakeGridType(graphene.ObjectType):
    project = graphene.Field(ProjectType)
    customer = graphene.Field(CustomerType)
    location_data = graphene.Field(LocationType)
    bom = graphene.List(graphene.String)
    crate_intake_ids = graphene.List(CrateType)

class ModuleIntakeGridPagesType(graphene.ObjectType):
    items = graphene.List(ModuleIntakeGridType)
    total_count = graphene.Int()
    has_next = graphene.Boolean()

# =====================================================
# ModuleIntakeDetails Type
# =====================================================
class ModuleIntakeDetailsType(DjangoObjectType):
    id = graphene.Int()
    customer_name = graphene.String()
    manufacturer_name = graphene.String()
    crate_name = graphene.String()
    project_number = graphene.String()
    ntp_date = graphene.DateTime()
    intake_by = graphene.String()
    location = graphene.Int()
    projects = graphene.Int()
    customer = graphene.Int()
    newcrateintake = graphene.Int()


    class Meta:
        model = ModuleIntakeDetails
        fields = "__all__"

    def resolve_customer_name(self, info):
        return self.customer.name if self.customer else None

    def resolve_manufacturer_name(self, info):
        return self.customer.name if self.customer else None

    def resolve_crate_name(self, info):
        return self.newcrateintake.crate_name if self.newcrateintake else None

    def resolve_project_number(self, info):
        return self.projects.number if self.projects else None
    
    def resolve_intake_by(self, info):
        return str(self.intake_by) if self.intake_by else None

    def resolve_ntp_date(self, info):
        workorder = WorkOrder.objects.filter(
            name=self.bom,
            project_id=self.projects.id if self.projects else None
        ).first()
        return workorder.start_datetime if workorder else None
    
    def resolve_location(self, info):
        return self.location.id if self.location else None

    def resolve_projects(self, info):
        return self.projects.id if self.projects else None

    def resolve_customer(self, info):
        return self.customer.id if self.customer else None

    def resolve_newcrateintake(self, info):
        return self.newcrateintake.id if self.newcrateintake else None
    
#------------------------------------------
#Pagination Type for ModuleIntakeDetails
#------------------------------------------

class ModuleIntakePageType(graphene.ObjectType):
    items = graphene.List(ModuleIntakeDetailsType)
    total_count = graphene.Int()
    has_next = graphene.Boolean()


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
    project=graphene.String()

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
        dt = (
            Note.objects
            .filter(parent_note=self)
            .aggregate(Max("datetime"))
            .get("datetime__max")
        )
        return dt or self.datetime

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
        return self.project_set.values_list("number", flat=True).first()
    
# =====================================================
# Note flag Type
# =====================================================
    
class NoteFlagType(DjangoObjectType):
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
    project=graphene.String()
    user = graphene.Int()
    owner = graphene.Int()
    note_type = graphene.Int()
    disposition = graphene.Int()

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
        dt = (
            Note.objects
            .filter(parent_note=self)
            .aggregate(Max("datetime"))
            .get("datetime__max")
        )
        return dt or self.datetime

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
        return self.project_set.values_list("number", flat=True).first()
    
    def resolve_user(self, info):
        return self.user.id if self.user else None

    def resolve_owner(self, info):
        return self.owner.id if self.owner else None

    def resolve_note_type(self, info):
        return self.note_type.id if self.note_type else None

    def resolve_disposition(self, info):
        return self.disposition.id if self.disposition else None
    

# =====================================================
# Pagination Type for flags
# =====================================================
    
class NotesFlagPageType(graphene.ObjectType):
    items = graphene.List(NoteFlagType)
    total_count = graphene.Int()
    has_next = graphene.Boolean()

    
# =====================================================
# Pagination Type
# =====================================================

class NotesPageType(graphene.ObjectType):
    items = graphene.List(NoteType)
    total_count = graphene.Int()
    has_next = graphene.Boolean()


# =====================================================
# Filter Input  (NEW)
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
    project_number = graphene.String()
    
# =====================================================
# CRATE INTAKE TYPES
# =====================================================


# crate Intake get customers
# Project Number Type
class ProjectNumberType(graphene.ObjectType):
    id = graphene.Int()
    number = graphene.String()

# Customer Type
class CustomerNewType(DjangoObjectType):
    id = graphene.Int()
    notes = graphene.List(NoteType)
    project_numbers = graphene.List(ProjectNumberType)
    url = graphene.String()

    class Meta:
        model = Customer
        fields = "__all__"

    def resolve_notes(self, info):
        return self.notes.all()

    def resolve_project_numbers(self, info):
        return [
            {
                "id": p.id,
                "number": p.number
            }
            for p in self.project_set.all()
        ]

    def resolve_url(self, info):
        request = info.context
        if request:
            return request.build_absolute_uri(f"/api/1.0/customers/{self.id}/")
        return f"/api/1.0/customers/{self.id}/"
    
# Customer Pagination
class CustomerPageType(graphene.ObjectType):
    count = graphene.Int()
    next = graphene.String()
    previous = graphene.String()
    results = graphene.List(CustomerNewType)
    
class CustomerListType(graphene.ObjectType):
    count = graphene.Int()
    results = graphene.List(CustomerNewType)
    
# Customer Filter
class CustomerFilterInput(graphene.InputObjectType):
    name = graphene.String()
    short_name = graphene.String()

# Crate Intake Get
class CrateIntakeType(graphene.ObjectType):
    id = graphene.Int()
    customer = graphene.Int()
    manufacturer = graphene.Int()
    project = graphene.Int()
    customer_name = graphene.String()
    manufacturer_name = graphene.String()
    project_number = graphene.String()
    created_by = graphene.String()
    created_on = graphene.String()
    crate_name = graphene.String()
    crate_intake_date = graphene.String()

    def resolve_customer(self, info):
        return self.customer.id if self.customer else None

    def resolve_manufacturer(self, info):
        return self.manufacturer if self.manufacturer else None

    def resolve_project(self, info):
        return self.project.id if self.project else None

    def resolve_customer_name(self, info):
        return self.customer.name if self.customer else None

    def resolve_manufacturer_name(self, info):
        return self.customer.name if self.manufacturer else None

    def resolve_project_number(self, info):
        return self.project.number if self.project else None

    def resolve_created_by(self, info):
        return self.created_by if self.created_by else None

    def resolve_created_on(self, info):
        return self.created_on.strftime("%Y-%m-%d") if self.created_on else None

    def resolve_crate_name(self, info):
        return self.crate_name

    def resolve_crate_intake_date(self, info):
        return str(self.crate_intake_date)
    
class CrateIntakePaginationType(graphene.ObjectType):
    count = graphene.Int()
    next = graphene.Int()
    previous = graphene.Int()
    results = graphene.List(CrateIntakeType)
    

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

    def resolve_notes(self, info, filters=None, limit=20, offset=0):
        user = info.context.user

        if not user.is_authenticated:
            user = User.objects.first()
            # raise GraphQLError("Authentication required")

        qs = Note.objects.all()
        q = Q()

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
            
            if filters.project_number:
                q &= Q(project__number=filters.project_number)

            if filters.search:
                q &= (
                    Q(subject__icontains=filters.search) |
                    Q(description__icontains=filters.search)
                )

        qs = qs.filter(q)

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

        if filters and filters.order_by:
            qs = qs.order_by(filters.order_by)

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
    
    
    # ============================================
    # FLAGS QUERY (NEW)
    # ============================================

    flags = graphene.Field(
        NotesFlagPageType,
        limit=graphene.Int(),
        offset=graphene.Int(),
    )

    def resolve_flags(self, info, limit=100, offset=0):
        MAX_LIMIT = 100

        if limit is None:
            limit = 100

        if limit > MAX_LIMIT:
            limit = MAX_LIMIT

        user = info.context.user

        if not user.is_authenticated:
            user = User.objects.first()

        qs = (
            Note.objects
            .filter(note_type__id=3)
            .exclude(disposition__complete=True)
        )

        read_subquery = NoteReadStatus.objects.filter(
            note=OuterRef("pk"),
            user=user
        )

        qs = (
            qs.annotate(read=Exists(read_subquery))
            .select_related("user", "owner", "note_type", "disposition")
            .prefetch_related("labels", "attachments", "tagged_users", "project_set")
            .distinct()
        )

        total_count = qs.count()

        items = qs[offset: offset + limit]
        has_next = offset + limit < total_count

        return NotesFlagPageType(
            items=items,
            total_count=total_count,
            has_next=has_next,
        )
        

    # ============================================
    # NEW GRAPHQL API (Same as your Django API)
    # ============================================

    failed_project_report = GenericScalar(
    start_date=graphene.String(required=True),
    end_date=graphene.String(required=True),
    is_mss=graphene.String(required=True),
    tsd_ids=graphene.String(),
    limit=graphene.Int(),
    offset=graphene.Int(),)

    # =====================================================
    # FAILED PROJECT REPORT (same logic as your DRF API)
    # =====================================================

    def resolve_failed_project_report(self,info,start_date,end_date,is_mss,tsd_ids=None,limit=10,offset=0):

        request = info.context

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT un.unit_id 
                FROM lsdb_unit_notes un 
                JOIN lsdb_note n ON un.note_id = n.id 
                WHERE n.note_type_id = 3
            """)
            unit_ids = [row[0] for row in cursor.fetchall()]

        # =====================================================
        # NON MSS
        # =====================================================

        if is_mss == "0":

            other_results = ProcedureResult.objects.filter(
                disposition_id__in=[3, 8, 19],
                unit_id__in=unit_ids,
                start_datetime__date__range=[start_date, end_date]
            ).distinct()

            excluded_units = Unit.objects.filter(
                Q(notes__subject__icontains="Quality issue") |
                Q(notes__subject__icontains="Mishandling damage") |
                Q(notes__subject__icontains="Pull Request")
            ).values_list("id", flat=True)

            pass_reports = ProcedureResult.objects.filter(
                disposition_id=2
            ).exclude(
                unit_id__in=excluded_units
            ).filter(
                unit__notes__note_type_id=3,
                start_datetime__date__range=[start_date, end_date]
            )

            pass_reports = pass_reports.order_by("-start_datetime")
            other_results = other_results.order_by("-start_datetime")

            total_pass = pass_reports.count()
            total_other = other_results.count()

            pass_reports = pass_reports[offset: offset + limit]
            other_results = other_results[offset: offset + limit]

            return {
                "pass_reports": FailedProjectReportSerializer(
                    pass_reports,
                    many=True,
                    context={"request": request}
                ).data,

                "other_results": FailedProjectReportSerializer(
                    other_results,
                    many=True,
                    context={"request": request}
                ).data,

                "pagination": {
                    "limit": limit,
                    "offset": offset,
                    "pass_total": total_pass,
                    "other_total": total_other,
                    "has_next": offset + limit < max(total_pass, total_other)
                }
            }

        # =====================================================
        # MSS LOGIC
        # =====================================================

        if is_mss == "1":

            if tsd_ids:
                tsd_ids = [int(x) for x in tsd_ids.split(",")]

                bases = ProcedureResult.objects.filter(
                    procedure_definition_id__in=[8, 20],
                    test_sequence_definition_id__in=tsd_ids
                )

            else:

                bases = ProcedureResult.objects.filter(
                    procedure_definition_id__in=[8, 20]
                )

            bases = bases.order_by("linear_execution_group").distinct()

            mss_response = []

            for base in bases:

                first_next = ProcedureResult.objects.filter(
                    unit_id=base.unit_id,
                    linear_execution_group__gt=base.linear_execution_group
                ).order_by("linear_execution_group").first()

                if not first_next:
                    continue

                if first_next.group_id == 45:

                    final_next = ProcedureResult.objects.filter(
                        unit_id=base.unit_id,
                        linear_execution_group__gt=first_next.linear_execution_group
                    ).order_by("linear_execution_group").first()

                else:
                    final_next = first_next

                if not final_next:
                    continue

                if not final_next.stepresult_set.filter(
                    measurementresult__date_time__range=(start_date, end_date)
                ).exists():
                    continue

                if final_next.disposition_id == 3:

                    if final_next.procedure_definition_id in [2, 3]:

                        mr = MeasurementResult.objects.filter(
                            step_result__procedure_result=base,
                            asset__name__isnull=False
                        ).select_related("asset").first()

                        final_next.asset_name = mr.asset.name if mr else None

                        mss_response.append(final_next)

                elif final_next.disposition_id in [2, 20]:

                    if (
                        final_next.procedure_definition_id in [2, 3]
                        and final_next.stepresult_set.filter(
                            measurementresult__result_defect_id__isnull=False
                        ).exists()
                    ):

                        mr = MeasurementResult.objects.filter(
                            step_result__procedure_result=base,
                            asset__name__isnull=False
                        ).select_related("asset").first()

                        final_next.asset_name = mr.asset.name if mr else None

                        mss_response.append(final_next)

            # ---------------------------
            # tsd data generation
            # ---------------------------

            tsd_dict = {
                obj.test_sequence_definition_id: obj.test_sequence_definition.name
                for obj in mss_response
            }

            tsd_data = [
                {"id": id_, "tsd_name": name}
                for id_, name in tsd_dict.items()
            ]

            total = len(mss_response)

            mss_response = mss_response[offset: offset + limit]

            return json.loads(json.dumps({
                "pass_reports": [],
                "other_results": MssFailedProjectReportSerializer(
                    mss_response,
                    many=True,
                    context={"request": request}
                ).data,
                "tsd_data": tsd_data,
                "pagination": {
                    "limit": limit,
                    "offset": offset,
                    "total": total,
                    "has_next": offset + limit < total
                }
            }, cls=DjangoJSONEncoder))
        


    # ---------------- MODULE INTAKE DETAILS ----------------
    details = graphene.Field(
    ModuleIntakeGridPagesType,
    limit=graphene.Int(),
    offset=graphene.Int(),)

    def resolve_details(self, info, limit=-1, offset=0):

        # ---------------- TOTAL COUNT ----------------
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT COUNT(DISTINCT p.id)
                FROM lsdb_project p
            """)
            total_count = cursor.fetchone()[0]


        # ---------------- MAIN QUERY WITH PAGINATION ----------------
        query = """
            SELECT DISTINCT p.id, p.number, p.customer_id
            FROM lsdb_project p
            ORDER BY p.id
        """

        if limit != -1:
            query += " LIMIT %s OFFSET %s"

        with connection.cursor() as cursor:
            if limit == -1:
                cursor.execute(query)
            else:
                cursor.execute(query, [limit, offset])

            projects = cursor.fetchall()

        has_next = False if limit == -1 else (offset + limit < total_count)

        result = []

        for project_id, project_number, customer_id in projects:


            # ---------------- CUSTOMER ----------------
            try:
                customer = Customer.objects.get(id=customer_id)
                customer_data = CustomerType(
                    customer_id=customer.id,
                    customer_name=customer.name
                )
            except Customer.DoesNotExist:
                customer_data = CustomerType(
                    customer_id=None,
                    customer_name="Unknown"
                )


            # ---------------- LOCATION ----------------
            try:
                project_log = LocationLog.objects.get(
                    project_id=project_id,
                    is_latest=True,
                    flag=2
                )

                if project_log.location_id:
                    try:
                        location = Location.objects.get(id=project_log.location_id)
                        location_data = LocationType(
                            location_id=location.id,
                            location_name=location.name
                        )
                    except Location.DoesNotExist:
                        location_data = LocationType(location_id=None, location_name=None)
                else:
                    location_data = LocationType(location_id=None, location_name=None)

            except LocationLog.DoesNotExist:
                location_data = LocationType(location_id=None, location_name=None)


            # ---------------- BOM ----------------
            workorders = WorkOrder.objects.filter(
                project_id=project_id
            ).values_list('name', flat=True)


            # ---------------- CRATES ----------------
            crates = NewCrateIntake.objects.filter(
                Q(project_id=project_id) |
                (Q(project_id__isnull=True) & Q(customer_id=customer_id))
            ).values('id', 'crate_name')

            crate_list = [
                CrateType(id=c['id'], crate_name=c['crate_name'])
                for c in crates
            ]

            result.append(
                ModuleIntakeGridType(
                    project=ProjectType(
                        project_id=project_id,
                        project_number=project_number
                    ),
                    customer=customer_data,
                    location_data=location_data,
                    bom=list(workorders),
                    crate_intake_ids=crate_list
                )
            )

        return ModuleIntakeGridPagesType(
            items=result,
            total_count=total_count,
            has_next=has_next
        )
    
    
    # ============================================
    # Module Intake QUERY (NEW)
    # ============================================

    module_intake_details = graphene.Field(
        ModuleIntakePageType,
        limit=graphene.Int(),
        offset=graphene.Int(),
    )

    def resolve_module_intake_details(self, info, limit=100, offset=0):
        MAX_LIMIT = 100

        if limit is None:
            limit = 100

        if limit > MAX_LIMIT:
            limit = MAX_LIMIT

        qs = ModuleIntakeDetails.objects.all().order_by('-intake_date')

        total_count = qs.count()
        items = qs[offset: offset + limit]

        return ModuleIntakePageType(
            items=items,
            total_count=total_count,
            has_next=offset + limit < total_count
        )

    # ============================================
    # Crate Intake QUERY (NEW)
    # ============================================


    # Crate Intake CUSTOMER QUERY
    customers = graphene.Field(
        CustomerListType,
        filters=CustomerFilterInput(),
    )

    customer = graphene.Field(
        CustomerNewType,
        id=graphene.Int(required=True)
    )
    
    def resolve_customer(self, info, id):
        return Customer.objects.get(id=id)

    def resolve_customers(self, info, filters=None):
        request = info.context

        qs = Customer.objects.all().prefetch_related("project_set", "notes").order_by("id")

        if filters:
            if filters.name:
                qs = qs.filter(name__icontains=filters.name)
            if filters.short_name:
                qs = qs.filter(short_name__icontains=filters.short_name)

        return CustomerListType(
            count=qs.count(),
            results=qs
        )
    
    # Crate Intake Get
    crate_intakes = graphene.Field(
    CrateIntakePaginationType,
    limit=graphene.Int(),
    offset=graphene.Int())

    def resolve_crate_intakes(self, info, limit=100, offset=0):
        queryset = (
            NewCrateIntake.objects
            .select_related("customer", "project")  
            .order_by('-crate_intake_date')
        )

        total_count = queryset.count()
        results = queryset[offset: offset + limit]

        return CrateIntakePaginationType(
            count=total_count,
            next=offset + limit if offset + limit < total_count else None,
            previous=max(offset - limit, 0) if offset > 0 else None,
            results=results
        )