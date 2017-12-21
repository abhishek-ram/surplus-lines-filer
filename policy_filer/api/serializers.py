from rest_framework import serializers
from policy_filer.api.models import Filing


class FilingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Filing
        fields = ('id', 'state', 'policy_number', 'action')