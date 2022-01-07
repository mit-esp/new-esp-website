from django.db.models import Count

from esp.models.course_scheduling_models import CourseSection
from esp.models.program_registration_models import ClassRegistration


class LotteryDisallowedError(Exception):
    pass


def run_program_lottery(program):
    # TODO: Actual lottery/preference-matching algorithm
    # This placeholder makes no distinction between class preference categories,
    # fills slots greedily, and also makes many database calls.
    if ClassRegistration.objects.filter(course_section__course__program_id=program.id).exists():
        raise LotteryDisallowedError("Course assignments already exist")
    registrations_count = 0
    for time_slot in program.time_slots.all():
        for section in CourseSection.objects.filter(time_slots__time_slot=time_slot).distinct():
            interested_students = (
                section.preferences.values("registration_id").annotate(num=Count("id")).order_by("num")
            )
            interested_students = interested_students.exclude(
                registration_id__in=ClassRegistration.objects.filter(
                    course_section__course_id=section.course_id
                ).values("program_registration_id")
            ).exclude(
                registration_id__in=ClassRegistration.objects.filter(
                    course_section__time_slots__time_slot=time_slot
                ).values("program_registration_id")
            )
            registrations = [
                ClassRegistration(
                    course_section=section, program_registration_id=student["registration_id"], created_by_lottery=True
                )
                for student in interested_students[:section.course.max_section_size]
            ]
            ClassRegistration.objects.bulk_create(registrations)
            registrations_count += len(registrations)
    return registrations_count
