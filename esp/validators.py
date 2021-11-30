from datetime import timedelta


from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


def validate_graduation_year(value):
    earliest_allowed = (timezone.now() - timedelta(years=50)).year
    latest_allowed = (timezone.now() + timedelta(years=15)).year
    if not earliest_allowed <= value <= latest_allowed:
        raise ValidationError(
            _('%(value)s is not a valid graduation year'),
            params={'value': value},
        )
