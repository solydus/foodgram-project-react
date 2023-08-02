from base64 import b64decode

from django.core.files.base import ContentFile
from rest_framework.serializers import ImageField


class Base64ImageField(ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64')
            ext = format.split('/')[-1]
            data = ContentFile(b64decode(imgstr), name='photo.' + ext)
        return super().to_internal_value(data)
