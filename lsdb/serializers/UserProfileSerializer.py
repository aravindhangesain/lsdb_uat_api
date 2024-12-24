from rest_framework import serializers

from lsdb.models import UserProfile
from lsdb.serializers.TemplateSerializer import UserProfileTemplateSerializer


class UserProfileSerializer(serializers.HyperlinkedModelSerializer):
    # username = serializers.ReadOnlyField(source='user.username')
    registration_status = serializers.SerializerMethodField()
    allowed_templates = UserProfileTemplateSerializer(many=True, required=False)

    def get_registration_status(self, obj):
        if obj.user_registration_status:
            return obj.user_registration_status.status
        else:
            return None

    class Meta:
        model = UserProfile
        fields = [
            'id',
            'url',
            # 'user',
            # 'username',
            'notes',
            'registration_comment',
            'administration_comment',
            'user_registration_status',
            'registration_status',
            'allowed_templates'
            # 'birth_date',
            # 'box_user',
        ]
