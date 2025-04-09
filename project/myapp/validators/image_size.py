
from django.core.validators import ValidationError


def validate_image(image): # custom validator
    file_size = image.file.size
    limit_mb = 5
    if file_size> limit_mb*1024*1024:
        raise ValidationError(f"Maximum Image size is{limit_mb}mb.")