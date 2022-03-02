from django import template

from common.constants import Weekday

register = template.Library()


@register.filter
def format_time_slots(time_slots):
    if not time_slots:
        return "Unscheduled"
    return ", ".join([format_time_slot(slot) for slot in time_slots])


def format_time_slot(slot):
    time_string = f"{format_time(slot[0])} - {format_time(slot[1])} ({Weekday(slot[0].weekday()).label})"
    return f"{time_string} in {slot[2]}"


def format_time(time):
    time_format = "%I:%M%p"
    return time.strftime(time_format).lstrip('0')
