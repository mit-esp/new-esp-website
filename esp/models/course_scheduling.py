from datetime import timedelta

from django.db import models

from common.models import BaseModel
from esp.constants import ClassroomTagCategory
from esp.models.program import Classroom, ClassroomTag, Course, TimeSlot


class ClassroomConstraint(BaseModel):
    """Generic model to represent a scheduling constraint, which may specify requirements on classroom tags"""
    course = models.ManyToManyField(Course, related_name="scheduling_constraints")
    # TODO: If `required_classroom_tag` is set, all classrooms scheduled for this course must have this tag
    required_classroom_tag = models.ForeignKey(
        ClassroomTag, related_name="scheduling_constraints", on_delete=models.PROTECT, null=True
    )
    # TODO: If `require_all_tags_same_category` is set, all classrooms must have tags in this category that match
    require_all_tags_same_category = models.CharField(choices=ClassroomTagCategory.choices, null=True, max_length=128)
    # TODO: If `require_all_tags_different_category` is set, no classrooms may have tags in this category that match
    require_all_tags_different_category = models.CharField(
        choices=ClassroomTagCategory.choices, null=True, max_length=128
    )

    # TODO: Other arbitrary constraint, not handled automatically but displayed on the scheduler interface
    constraint = models.CharField(max_length=256)


class CourseSection(BaseModel):
    """
    CourseSection represents a particular enrollment section of a Course.
    Courses that meet multiple times still have a single CourseSection for all meetings of the same group of students,
    which will be related to multiple ClassroomTimeSlots.
    """
    course = models.ForeignKey(Course, related_name="sections", on_delete=models.PROTECT)

    def get_section_times(self):
        time_slots = self.time_slots.order_by("time_slot__start_time").values(
            "time_slot__start_time", "time_slot__end_time"
        )
        start_time = None
        end_time = None
        times = []
        for slot in time_slots:
            if not start_time:
                start_time = slot["time_slot__start_time"]
            if end_time and (
                slot["time_slot__start_time"]
                > end_time + timedelta(minutes=self.course.program.time_block_minutes - 1)
            ):
                times.append((start_time, end_time))
                start_time = slot["time_slot__start_time"]
            end_time = slot["time_slot__end_time"]
        times.append((start_time, end_time))
        return times

    def __str__(self):
        return f"{self.course.display_id} section"


class ClassroomTimeSlot(BaseModel):
    """
    A ClassroomTimeSlot instance exists for a given classroom, time slot pair
        only if the classroom is reserved by ESP for that time slot.
    If course_section is non-null, the classroom slot is booked for that class section.
    """
    classroom = models.ForeignKey(Classroom, related_name="time_slots", on_delete=models.CASCADE)
    time_slot = models.ForeignKey(TimeSlot, related_name="classrooms", on_delete=models.PROTECT)
    course_section = models.ForeignKey(CourseSection, related_name="time_slots", on_delete=models.PROTECT, null=True)
