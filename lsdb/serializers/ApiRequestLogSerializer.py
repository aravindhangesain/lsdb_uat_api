from rest_framework import serializers
from rest_framework_tracking.models import APIRequestLog

class ApiRequestLogSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()
    def get_username(self,obj):
        if obj.user:
            return obj.user.username
        else:
            return None
    # remote_addr = serializers.SerializerMethodField()
    #
    # def get_remote_addr(self, instance):
    #     print(self.remote_addr)

    class Meta:
        model = APIRequestLog
        # fields = '__all__'
        fields = (
            'id',
            'url',
            'requested_at',
            'user',
            'username',
            'path',
            'view',
            'response_ms',
            'view_method',
            'remote_addr',
            'host',
            'method',
             # 'query_params',
             # 'data',
             # 'response',
            'errors',
            'status_code',
        )
        # exclude=('data','query_params','response','remote_addr')

class ApiRequestLogDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = APIRequestLog
        fields = '__all__'
        # exclude=('data','query_params','response',)
