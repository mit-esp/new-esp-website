from django.db import models

from common.models import BaseModel
from esp.models.program import Classroom, ClassroomTag, Course, TimeSlot


class ResourceType(BaseModel):
    name = models.CharField(max_length=512)

    def __str__(self):
        return self.name


class ClassroomResource(BaseModel):
    """ClassroomResource represents a specific resource that exists in a specific classroom"""
    classroom = models.ForeignKey(Classroom, related_name="resources", on_delete=models.CASCADE)
    resource_type = models.ForeignKey(ResourceType, related_name="classrooms", on_delete=models.PROTECT)
    quantity = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.classroom}: {self.resource_type}"


class ResourceRequest(BaseModel):
    course = models.ForeignKey(Course, related_name="resource_requests", on_delete=models.CASCADE)
    resource_type = models.ForeignKey(ResourceType, related_name="requests", on_delete=models.PROTECT)
    quantity = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.course}: {self.resource_type}" + (f"({self.quantity})" if self.quantity else "")


class SchedulingConstraint(BaseModel):
    course = models.ManyToManyField(Course, related_name="scheduling_constraints")
    required_classroom_tag = models.ForeignKey(
        ClassroomTag, related_name="scheduling_constraints", on_delete=models.PROTECT, null=True
    )
    constraint = models.CharField(max_length=256)


class ClassroomTimeSlot(BaseModel):
    classroom = models.ForeignKey(Classroom, related_name="time_slots", on_delete=models.CASCADE)
    time_slot = models.ForeignKey(TimeSlot, related_name="classrooms", on_delete=models.PROTECT)


class ClassSection(BaseModel):
    """
    ClassSection represents a particular enrollment section of a Course, in a specific time slot and place.
    Programs that meet multiple times still have a single ClassSection for all meetings of the same group of students.
    """
    course = models.ForeignKey(Course, related_name="sections", on_delete=models.PROTECT)
    classroom_time_slot = models.OneToOneField(
        ClassroomTimeSlot, related_name="class_section", on_delete=models.PROTECT, null=True
    )

    def __str__(self):
        return f"{self.course.display_id}: {self.classroom_time_slot}"
