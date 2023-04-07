from dateutil.relativedelta import relativedelta
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


def validate_graduation_year(value):
    earliest_allowed = (timezone.now() - relativedelta(years=round(100))).year  # 100 years
    latest_allowed = (timezone.now() + relativedelta(years=round(15))).year  # 15 years
    if not earliest_allowed <= value <= latest_allowed:
        raise ValidationError(
            _('%(value)s is not a valid graduation year. Must be between %(earliest_allowed)s - %(latest_allowed)s'),
            params={'value': value, 'earliest_allowed': earliest_allowed, 'latest_allowed': latest_allowed},
        )
