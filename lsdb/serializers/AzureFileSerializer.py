from rest_framework import serializers
from lsdb.models import AzureFile
from django.core.exceptions import ObjectDoesNotExist
import hashlib

class AzureFileSerializer(serializers.HyperlinkedModelSerializer):
    # name = serializers.SerializerMethodField()
    #
    # def get_name(self, obj):
    #     if obj.file:
    #         return obj.file.name
    #     else:
    #         return None

    def to_representation(self, instance):
        """Convert `file location` to download URL."""
        ret = super().to_representation(instance)
        ret['file'] = ret['url'] + 'download/'
        return ret

    def create(self, validated_data):
        # hasher = hashlib.new(validated_data.get('hash_algorithm'))
        hasher = hashlib.new('sha256')
        file_data = validated_data.get('file')
        for buf in file_data.chunks(chunk_size = 65536):
            hasher.update(buf)
        validated_data['hash'] = hasher.hexdigest()
        validated_data['hash_algorithm'] = 'sha256'
        validated_data['length'] = file_data.size
        validated_data['name'] = file_data.name
        try:
            file = AzureFile.objects.get(
                hash=validated_data.get('hash'),
                name=validated_data.get('name'),
                blob_container=validated_data.get('blob_container'),
            )
            # Deprecated behavior, we now give you the previous file
            # message =  "file with Name: {} and {} Hash: {} already exists in Container: {}".format(
            #     validated_data.get('name'),
            #     validated_data.get('hash_algorithm'),
            #     validated_data.get('hash'),
            #     validated_data.get('blob_container',None)
            # )
            # raise serializers.ValidationError(message)
            # should throw 303 here for client to handle
        except AzureFile.DoesNotExist:
            file = AzureFile.objects.create(**validated_data)
        return file

    class Meta:
        model = AzureFile
        fields = [
            'id',
            'url',
            'file',
            'name',
            'uploaded_datetime',
            'hash_algorithm',
            'hash',
            'length',
            # TODO: Determine if we need this
            'blob_container',
            'expires',
        ]
        read_only_fields = [
            'name',
            'hash',
            'length',
            'expires',
        ]
