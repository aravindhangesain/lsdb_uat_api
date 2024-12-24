from rest_framework import serializers
from lsdb.models import Asset
from lsdb.utils.NoteUtils import get_note_counts


class AssetSerializer(serializers.HyperlinkedModelSerializer):
    location_name = serializers.ReadOnlyField(source='location.name')
    disposition_name = serializers.ReadOnlyField(source='disposition.name')
    # asset_type_name = serializers.ReadOnlyField(source='asset_type.name')
    notes = serializers.SerializerMethodField()

    def get_notes(self, obj):
        user = self.context.get('request').user
        return get_note_counts(user,obj)


    class Meta:
        model = Asset
        fields = [
            'id',
            'url',
            'name',
            'description',
            'location',
            'location_name',
            'last_action_datetime',
            # 'asset_type_name',
            'asset_types',
            'disposition_name',
            'disposition',
            'notes',
        ]
