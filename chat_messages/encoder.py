
from django.core.serializers.json import DjangoJSONEncoder
import uuid
class CustomJSONEncoder(DjangoJSONEncoder):
    def default(self, o):
        if isinstance(o, uuid.UUID):
            return str(o) 
        return super().default(o)