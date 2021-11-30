from datetime import timedelta


from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


def validate_graduation_year(value):
    earliest_allowed = (timezone.now() - timedelta(days=round(50 * 365.25))).year  # 50 years
    latest_allowed = (timezone.now() + timedelta(days=round(15 * 365.25))).year  # 15 years
    if not earliest_allowed <= value <= latest_allowed:
        raise ValidationError(
            _('%(value)s is not a valid graduation year. Must be between %(earliest_allowed)s - %(latest_allowed)s'),
            params={'value': value, 'earliest_allowed': earliest_allowed, 'latest_allowed': latest_allowed},
        )
