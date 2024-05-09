import os
from django.core.exceptions import ValidationError

def allow_only_images_validator(file):
    extension = os.path.splitext(file.name)[1]
    print(extension)
    valid_extensions = ['.jpg', '.png', '.jpeg']
    if not extension.lower() in valid_extensions:
        raise ValidationError('Unsupported file extension. Allowed extensions: ' + str(valid_extensions))