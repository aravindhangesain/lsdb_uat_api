from rest_framework import serializers
from django.contrib.auth.models import User

from lsdb.models import UserProfile
from lsdb.serializers import UserProfileSerializer

class UserListSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = User
        fields = [
            'id',
            'url',
            'email',
            'username',
            'first_name',
            'last_name',
        ]
