import base64
import os
import uuid

from django.conf import settings
from rest_framework import serializers


class Base64ImageField(serializers.ImageField):
    """
    Пользовательское поле для обработки изображений в формате base64.
    """

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            decoded_image = base64.b64decode(data.split(';base64,')[1])
            filename = str(uuid.uuid4()) + '.jpg'
            with open(os.path.join(settings.MEDIA_ROOT, filename), 'wb') as f:
                f.write(decoded_image)
            return filename
        return super().to_internal_value(data)
