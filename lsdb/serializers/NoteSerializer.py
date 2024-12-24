from django.contrib.auth.models import User
from django.db.models import Max

from rest_framework import serializers

from lsdb.models import Label
from lsdb.serializers.LabelSerializer import LabelSerializer
from lsdb.models import AzureFile
from lsdb.serializers import AzureFileSerializer
from lsdb.models import Note

class ObjectSerializer(serializers.BaseSerializer):
    def to_representation(self, instance):
        return {
            'model_name': instance._meta.model_name,
            'id':instance.id,
            'str':str(instance.__str__())
        }

class NoteSerializer(serializers.ModelSerializer):
    attachments = AzureFileSerializer(AzureFile.objects.all(), many=True, read_only=True)
    labels = LabelSerializer(Label.objects.all(), many=True, read_only=True)
    tagged_users = serializers.SerializerMethodField()
    owner_name = serializers.ReadOnlyField(source='owner.username')
    username = serializers.ReadOnlyField(source='user.username')
    note_type_name = serializers.ReadOnlyField(source='note_type.name')
    disposition_name = serializers.ReadOnlyField(source='disposition.name')
    disposition_complete = serializers.ReadOnlyField(source='disposition.complete')
    read = serializers.SerializerMethodField()
    last_update_datetime = serializers.SerializerMethodField()
    parent_objects = serializers.SerializerMethodField()

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        obj = Note.objects.create(**validated_data)
        obj.save()
        return obj

    def get_last_update_datetime(self, obj):
        # need highest date of all chlid notes:
        date_time = Note.objects.filter(parent_note=obj).aggregate(Max('datetime')).get('datetime__max')
        if date_time:
            return date_time
        else:
            return obj.datetime

    def get_read(self, obj):
        user = self.context.get('request').user
        return bool(obj.notereadstatus_set.filter(user=user).count())

    def get_parent_objects(self, obj):
        # because we don't always know what models have a realtion to
        # us, we need to interrogate the _meta
        parent_objects = []
        related_objects = obj._meta.related_objects
        for object in related_objects:
            if object.remote_field.name == 'notes':
                # we know we're looking at a reverse accessor to notes:
                parents = object.remote_field.model.objects.filter(notes__in=[obj.id])
                for parent in parents:
                    serializer = ObjectSerializer(parent)
                    parent_objects.append(serializer.data)
        return parent_objects

    def get_tagged_users(self, obj):
        queryset = obj.tagged_users.all()
        userStruct = []
        for user in queryset:
            temp = {
                "id": user.id,
                "username": user.username,
            }
            userStruct.append(temp)
        return userStruct

    class Meta:
        model = Note
        fields = [
            'id',
            'url',
            'user',
            'username',
            'owner',
            'owner_name',
            'parent_note',
            'datetime',
            'last_update_datetime',
            'subject',
            'text',
            'note_type',
            'note_type_name',
            'disposition',
            'disposition_name',
            'disposition_complete',
            'read',
            # 'organization',
            'attachments',
            'labels',
            'groups',
            'tagged_users',
            'parent_objects',
        ]
