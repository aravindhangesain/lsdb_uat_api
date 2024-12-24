from django.contrib.auth.models import User
from django.apps import apps
from django.db import IntegrityError, transaction
from django.conf import settings

from lsdb.models import Note
from lsdb.models import NoteType
from lsdb.models import NoteReadStatus
from lsdb.models import Organization
from lsdb.models import Disposition
from lsdb.models import ProcedureResult
from lsdb.models import Unit

# def create_note(model, pk, user, subject, text, note_type,
#         disposition=None, parent_note=None, organization=None):
# This is the universal create note

def get_note_link(obj):
    routes = {
        'Flag':'/engineering/engineering_agenda',
        'Support Ticket':'/engineering/engineering_agenda',
        'Task':'/operations_management/ops_agenda',
        'Note':'/profile_management/my_agenda'
    }
    url = '{}{}/{}'.format(settings.CLIENT_HOST,routes.get(obj.note_type.name),obj.id)
    return url

@transaction.atomic
def create_note(**kwargs):
    # these are for therering a note:
    model_name = kwargs.pop('model')
    target_id = kwargs.pop('pk')

    type = kwargs.pop('note_type')
    note_type = NoteType.objects.get(id=type)

    # TODO: Parse note body to find tagged_users

    note = Note.objects.create(
        **kwargs,
        note_type=note_type,
    )
    # TODO: add the parsed users from above to the table
    # for user in tagged_users:
    #     note.tagged_users.add(user)
    # New notes should be created as read by the writer of the note:
    NoteReadStatus.objects.create(
        user = kwargs.get('user'),
        note = note
    )
    if model_name:
        try:
            model = apps.get_app_config('lsdb').get_model(model_name)
        except Exception as e:
                return e
        obj = model.objects.get(pk=target_id)
        obj.notes.add(note)
    return note

# This gets called from Serializers that need counts:
def get_note_counts(user, obj):
    # from lsdb.models import NoteType
    note_counts = []
    queryset = obj.notes.all()
    note_list = queryset.values_list('note_type__name').distinct()
    children = Note.objects.filter(parent_note__in=queryset).distinct()
    type_list=[]
    for note in note_list:
        if note[0] not in type_list:
            type_list.append(note[0])
    if note_list:
        for note_type in type_list:
            # TODO: optomize this using aggregates
            type_dict={'unread_count':0,"active_count":0,"closed_count":0}
            type_dict['type_name'] = str(note_type)
            # all notes on this object of this type
            these_notes = queryset.filter(note_type__name=note_type).distinct()
            active_notes = queryset.filter(note_type__name=note_type, disposition__complete=False).distinct()
            closed_notes = queryset.filter(note_type__name=note_type, disposition__complete=True).distinct()
            null_notes = queryset.filter(note_type__name=note_type, disposition__isnull=True).distinct()
            type_dict['count'] = these_notes.count()
            type_dict['active_count'] = active_notes.count() + null_notes.count()
            type_dict['closed_count'] = closed_notes.count()
            # all children of notes of this type
            child_queryset = children.filter(parent_note__in=these_notes).distinct()
            # KLUGE: this might get unwieldy
            for note in these_notes:
                if these_notes.filter(read_status =user, id=note.id).count():
                    # This note is read, check the kids:
                    if child_queryset.filter(read_status = user, parent_note = note).count() != child_queryset.filter(parent_note = note).count():
                        # one or more childern are unread
                        type_dict['unread_count'] += 1
                else:
                    # this note is unread
                    type_dict['unread_count'] += 1
            note_counts.append(type_dict)
    return note_counts
