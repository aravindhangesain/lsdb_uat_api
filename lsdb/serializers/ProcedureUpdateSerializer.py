from rest_framework import serializers

class ProcedureUpdateSerializer(serializers.Serializer):
    serial_numbers = serializers.ListField(
        child=serializers.CharField(max_length=255)
    )
