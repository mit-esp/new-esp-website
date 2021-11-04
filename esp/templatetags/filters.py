from django import template

register = template.Library()


@register.filter
def format_time_slots(time_slots):
    if not time_slots:
        return ""
    time_format = "%I:%M%p"
    return ", ".join([
        f"{slot[0].strftime(time_format).lstrip('0')} - {slot[0].strftime(time_format).lstrip('0')}"
        for slot in time_slots
    ])
