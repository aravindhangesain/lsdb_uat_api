from django.contrib.auth.models import User
from django.db import transaction
from rest_framework import serializers

from lsdb.models import UserProfile
from lsdb.serializers import UserProfileSerializer
from lsdb.serializers.TemplateSerializer import UserProfileTemplateSerializer


class EditUserSerializer(serializers.HyperlinkedModelSerializer):
    id = serializers.IntegerField(read_only=True)
    allowed_templates = serializers.SerializerMethodField()

    def get_allowed_templates(self, obj: User):
        allowed_templates = obj.userprofile.allowed_templates.all()
        serializer = UserProfileTemplateSerializer(allowed_templates, many=True, context=self.context)

        return serializer.data

    class Meta:
        model = User
        fields = [
            'id',
            'first_name',
            'last_name',
            'allowed_templates'
        ]


class UserSerializer(serializers.HyperlinkedModelSerializer):
    userprofile = UserProfileSerializer(many=False)
    groups = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            # 'user',
            'is_active',
            'is_staff',
            'is_superuser',
            'date_joined',
            'url',
            'username',
            'first_name',
            'last_name',
            'groups',
            'userprofile',
            'password',
        ]

    def get_groups(self, obj):
        ids = []
        for id in obj.group_set.all().values('id'):
            ids.append(id.get('id'))
        return ids

    @transaction.atomic
    def create(self, validated_data):
        profile_data = validated_data.pop('userprofile')
        password = validated_data.pop('password')
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        profile_data['user'] = user
        UserProfile.objects.create(**profile_data)
        return user

    @transaction.atomic
    def update(self, instance, validated_data):
        profile_data = validated_data.pop('userprofile', None)
        # Update UserProfile data
        try:
            if not instance.userprofile:
                pass
        except:
            UserProfile.objects.create(user=instance, **profile_data)

        if profile_data:
            # Update Profile data
            ins = instance.userprofile
            ins.notes = profile_data.get('notes', instance.userprofile.notes)
            ins.registration_comment = profile_data.get('registration_comment',
                                                        instance.userprofile.registration_comment)
            ins.administration_comment = profile_data.get('administration_comment',
                                                          instance.userprofile.administration_comment)
            ins.user_registration_status = profile_data.get('user_registration_status',
                                                            instance.userprofile.user_registration_status)
            ins.save()

        # update user data by hand:
        if validated_data.get('password', instance.password) != instance.password:
            instance.set_password(validated_data.get('password'))

        if self.context.get('request').user.is_superuser:
            # Superuser API access:
            instance.email = validated_data.get('email', instance.email)
            instance.username = validated_data.get('username', instance.username)
            instance.is_active = validated_data.get('is_active', instance.is_active)
            instance.is_staff = validated_data.get('is_staff', instance.is_staff)
            instance.is_superuser = validated_data.get('is_superuser', instance.is_superuser)

        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.save()

        return instance
