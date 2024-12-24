from rest_framework import serializers
from lsdb.models import UserRegistrationStatus

class UserRegistrationStatusSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = UserRegistrationStatus
        fields = [
            'id',
            'url',
            'status',
            'description',
        ]
