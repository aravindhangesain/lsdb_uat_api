from lsdb.models import NotificationQueue

class NotificationQueueSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = NotificationQueue
        fields = '__all__'
