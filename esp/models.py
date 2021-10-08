from django.db import models
from django.db.models import Max

from common.constants import Weekday
from common.models import BaseModel, User
from esp.constants import (CourseRoleType, CourseStatus, ProgramType,
                           RegistrationStep)


class PreferenceEntryConfiguration(BaseModel):
    """PreferenceEntryConfiguration represents a set of stages and steps for student class preference entry."""
    saved_as_preset = models.BooleanField(default=False)
    name = models.CharField(max_length=512, null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name


class Program(BaseModel):
    """Program represents an ESP program instance, e.g. Splash 2021"""
    preference_entry_configuration = models.ForeignKey(
        PreferenceEntryConfiguration, on_delete=models.PROTECT, related_name="+", null=True
    )
    name = models.CharField(max_length=512)
    program_type = models.CharField(choices=ProgramType.choices, max_length=128, null=True, blank=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    description = models.TextField(null=True)
    notes = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name


class Course(BaseModel):
    """
    Course represents an ESP class in a specific program (named to avoid reserved word 'class' conflicts).
    It is still referred to as 'class' in urls and on the frontend to match existing terminology.
    """
    program = models.ForeignKey(Program, related_name="courses", on_delete=models.PROTECT)
    name = models.CharField(max_length=2048)
    display_id = models.BigIntegerField(null=True, blank=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    description = models.TextField()
    max_size = models.IntegerField()
    prerequisites = models.TextField(default="None", blank=True)

    status = models.CharField(choices=CourseStatus.choices, max_length=32, default=CourseStatus.unreviewed)
    notes = models.TextField(null=True, blank=True)
    planned_purchases = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.display_id}: {self.name} ({self.program})"

    def save(self, *args, **kwargs):
        if not self.display_id:
            self.display_id = self.get_next_display_id()
        super().save(*args, **kwargs)

    @classmethod
    def get_next_display_id(cls):
        base_display_id = 314
        if not cls.objects.exists():
            return base_display_id
        return cls.objects.aggregate(Max("display_id"))["display_id__max"] + 1


class CourseRole(BaseModel):
    course = models.ForeignKey(Course, related_name="roles", on_delete=models.PROTECT)
    user = models.ForeignKey(User, related_name="course_roles", on_delete=models.PROTECT)
    role = models.CharField(choices=CourseRoleType.choices, max_length=32)


class Classroom(BaseModel):
    name = models.CharField(max_length=512)
    description = models.TextField(null=True, blank=True)
    max_occupants = models.IntegerField()

    def __str__(self):
        return self.name


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


class TimeSlot(BaseModel):
    program = models.ForeignKey(Program, related_name="time_slots", on_delete=models.PROTECT)
    day = models.CharField(choices=Weekday.choices, max_length=16, null=True)  # Required only for multi-day events
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        start = self.start_time.strftime('%I:%M%p').lstrip('0')
        end = self.end_time.strftime('%I:%M%p').lstrip('0')
        return f"{start} - {end}" + (f"({self.get_day_display()})" if self.day else "")


class ClassSection(BaseModel):
    """
    ClassSection represents a particular enrollment section of a Course, with a (clock) time and place.
    Programs that meet multiple times still have a single ClassSection for all meetings of the same group of students.
    """
    course = models.ForeignKey(Course, related_name="sections", on_delete=models.PROTECT)
    classroom = models.ForeignKey(Classroom, related_name="sections", on_delete=models.PROTECT, null=True, blank=True)
    time_slot = models.ForeignKey(TimeSlot, related_name="sections", on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.course.display_id}: {self.time_slot}"


class ProgramStage(BaseModel):
    """ProgramStage represents configuration for a program stage, e.g. 'Initiation' or 'Post-Lottery'"""
    program = models.ForeignKey(Program, related_name="stages", on_delete=models.PROTECT)
    name = models.CharField(max_length=256)
    index = models.IntegerField(default=0)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    description = models.TextField(null=True, blank=True)

    class Meta(BaseModel.Meta):
        constraints = [models.UniqueConstraint(fields=("program_id", "index"), name="unique_program_stage_index")]

    def __str__(self):
        return f"{self.program}: {self.name}"


class ProgramRegistrationStep(BaseModel):
    """ProgramRegistrationStep represents config for a single student interaction step within a program stage."""
    program_stage = models.ForeignKey(ProgramStage, related_name="steps", on_delete=models.PROTECT)
    display_name = models.CharField(max_length=512, null=True, blank=True)
    step_key = models.CharField(choices=RegistrationStep.choices, max_length=256)
    required_for_stage_completion = models.BooleanField(default=True)
    description = models.TextField(null=True, blank=True)

    class Meta(BaseModel.Meta):
        constraints = [
            models.UniqueConstraint(fields=("program_stage_id", "step_key"), name="unique_program_stage_step")
        ]

    def __str__(self):
        return f"{self.program_stage} - {self.display_name or self.get_step_key_display()}"


class ProgramRegistration(BaseModel):
    """ProgramRegistration represents a user's registration for a program."""
    program = models.ForeignKey(Program, related_name="registrations", on_delete=models.PROTECT)
    program_stage = models.ForeignKey(ProgramStage, on_delete=models.PROTECT, related_name="registrations")
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="registrations")

    def __str__(self):
        return f"{self.program} registration for {self.user}"


class PreferenceEntryRound(BaseModel):
    preference_entry_configuration = models.ForeignKey(
        PreferenceEntryConfiguration, on_delete=models.PROTECT, related_name="rounds"
    )
    index = models.IntegerField(default=0)
    title = models.CharField(max_length=512, null=True, blank=True)
    help_text = models.TextField()

    class Meta(BaseModel.Meta):
        constraints = [
            models.UniqueConstraint(
                fields=("preference_entry_configuration_id", "index"), name="unique_preference_entry_round_index"
            )
        ]

    def __str__(self):
        return f"{self.title} (Round {self.index})"


class PreferenceEntryCategory(BaseModel):
    preference_entry_round = models.ForeignKey(
        PreferenceEntryRound, related_name="categories", on_delete=models.PROTECT
    )
    tag = models.CharField(max_length=512)
    has_integer_value = models.BooleanField(default=False)
    max_value = models.IntegerField(null=True, blank=True)
    max_value_sum = models.IntegerField(null=True, blank=True)
    help_text = models.TextField()

    def __str__(self):
        return self.tag


class ClassPreference(BaseModel):
    """ClassPreference represents a preference entry category that a user has applied to a class section."""
    registration = models.ForeignKey(ProgramRegistration, related_name="preferences", on_delete=models.PROTECT)
    class_section = models.ForeignKey(ClassSection, related_name="preferences", on_delete=models.PROTECT)
    category = models.ForeignKey(PreferenceEntryCategory, related_name="preferences", on_delete=models.PROTECT)
    value = models.IntegerField(null=True)

    def __str__(self):
        return f"{self.registration} - {self.category} preference"


class ProgramTag(BaseModel):
    program = models.ForeignKey(Program, on_delete=models.PROTECT, related_name="tags")
    tag = models.CharField(max_length=256)

    def __str__(self):
        return self.tag


class CourseTag(BaseModel):
    course = models.ForeignKey(Course, on_delete=models.PROTECT, related_name="tags")
    tag = models.CharField(max_length=256)

    def __str__(self):
        return self.tag
