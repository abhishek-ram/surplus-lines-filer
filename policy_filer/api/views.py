from rest_framework.generics import ListCreateAPIView
from policy_filer.api.models import Filing
from policy_filer.api.serializers import FilingSerializer


class FilingLC(ListCreateAPIView):
    queryset = Filing.objects.all()

    def get_serializer(self, *args, **kwargs):
        kwargs['context'] = self.get_serializer_context()
        kwargs['many'] = True
        return FilingSerializer(*args, **kwargs)
