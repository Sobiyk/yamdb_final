from django.utils import timezone
from rest_framework.validators import ValidationError


def year_validator(value):
    if value > timezone.now().year:
        raise ValidationError(
            ('Некорректная дата!'),
            params={'value': value}
        )
