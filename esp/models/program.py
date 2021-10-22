from django.db import models
from django.db.models import Max
from django.utils import timezone

from common.constants import GradeLevel, Weekday
from common.models import BaseModel
from esp.constants import (CourseDifficulty, CourseStatus, ProgramType,
                           RegistrationStep)


class ProgramConfiguration(BaseModel):
    """ProgramConfiguration represents a set of stages and steps for student class preference entry."""
    saved_as_preset = models.BooleanField(default=False)
    name = models.CharField(max_length=512, null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name


class Program(BaseModel):
    """Program represents an ESP program instance, e.g. Splash 2021"""
    program_configuration = models.ForeignKey(
        ProgramConfiguration, on_delete=models.PROTECT, related_name="+", null=True
    )
    name = models.CharField(max_length=512)
    program_type = models.CharField(choices=ProgramType.choices, max_length=128, null=True, blank=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    min_grade_level = models.IntegerField(choices=GradeLevel.choices, default=7)
    max_grade_level = models.IntegerField(choices=GradeLevel.choices, default=12)
    description = models.TextField(null=True)
    notes = models.TextField(null=True, blank=True)

    show_to_students_on = models.DateTimeField()
    hide_from_students_on = models.DateTimeField()
    show_to_teachers_on = models.DateTimeField()
    hide_from_teachers_on = models.DateTimeField()
    show_to_volunteers_on = models.DateTimeField()
    hide_from_volunteers_on = models.DateTimeField()

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
    duration_minutes = models.IntegerField(default=60)
    prerequisites = models.TextField(default="None", blank=True)
    min_grade_level = models.IntegerField(choices=GradeLevel.choices, default=GradeLevel.seventh)
    max_grade_level = models.IntegerField(choices=GradeLevel.choices, default=GradeLevel.twelfth)
    difficulty = models.IntegerField(choices=CourseDifficulty.choices, default=CourseDifficulty.easy)

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


class TimeSlot(BaseModel):
    program = models.ForeignKey(Program, related_name="time_slots", on_delete=models.PROTECT)
    day = models.IntegerField(choices=Weekday.choices, null=True, blank=True)
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        start = self.start_time.strftime('%I:%M%p').lstrip('0')
        end = self.end_time.strftime('%I:%M%p').lstrip('0')
        return f"{start} - {end}" + (f" ({self.get_day_display()})" if self.day else "")

    class Meta(BaseModel.Meta):
        ordering = ("day", "start_time")


#######################
# Program configuration
#######################
class ProgramStage(BaseModel):
    """ProgramStage represents configuration for a program stage, e.g. 'Initiation' or 'Post-Lottery'"""
    program = models.ForeignKey(Program, related_name="stages", on_delete=models.PROTECT)
    name = models.CharField(max_length=256)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    manually_activated = models.BooleanField(default=False, blank=True)
    manually_hidden = models.BooleanField(default=False, blank=True)

    description = models.TextField(null=True, blank=True)

    class Meta(BaseModel.Meta):
        order_with_respect_to = "program"

    def __str__(self):
        return f"{self.program}: {self.name}"

    def is_active(self):
        return (
            ((self.start_date < timezone.now() < self.end_date) and not self.manually_hidden)
            or self.manually_activated
        )


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


class PreferenceEntryRound(BaseModel):
    program_configuration = models.ForeignKey(
        ProgramConfiguration, on_delete=models.PROTECT, related_name="rounds"
    )
    title = models.CharField(max_length=512, null=True, blank=True)
    help_text = models.TextField()
    group_sections_by_course = models.BooleanField(default=False)
    applied_category_filter = models.CharField(max_length=512, null=True, blank=True)

    class Meta(BaseModel.Meta):
        order_with_respect_to = "program_configuration_id"

    def __str__(self):
        return f"{self.title} (Round {self._order})"


class PreferenceEntryCategory(BaseModel):
    preference_entry_round = models.ForeignKey(
        PreferenceEntryRound, related_name="categories", on_delete=models.PROTECT
    )
    tag = models.CharField(max_length=512)
    pre_add_display_name = models.CharField(max_length=512, null=True, blank=True)
    post_add_display_name = models.CharField(max_length=512, null=True, blank=True)
    max_count = models.IntegerField(null=True, blank=True)
    min_count = models.IntegerField(null=True, blank=True)
    help_text = models.TextField()

    def __str__(self):
        return self.tag


class Classroom(BaseModel):
    name = models.CharField(max_length=512)
    description = models.TextField(null=True, blank=True)
    max_occupants = models.IntegerField()

    def __str__(self):
        return self.name


class ClassSection(BaseModel):
    """
    ClassSection represents a particular enrollment section of a Course, in a specific time slot and place.
    Programs that meet multiple times still have a single ClassSection for all meetings of the same group of students.
    """
    course = models.ForeignKey(Course, related_name="sections", on_delete=models.PROTECT)
    classroom = models.ForeignKey(Classroom, related_name="sections", on_delete=models.PROTECT, null=True, blank=True)
    time_slot = models.ForeignKey(TimeSlot, related_name="sections", on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.course.display_id}: {self.time_slot}"


class ProgramTag(BaseModel):
    program = models.ManyToManyField(Program, related_name="tags")
    tag = models.CharField(max_length=256)

    def __str__(self):
        return self.tag


class CourseTag(BaseModel):
    course = models.ManyToManyField(Course, related_name="tags")
    tag = models.CharField(max_length=256)
    display_name = models.CharField(max_length=256, null=True, blank=True)
    is_category = models.BooleanField(default=False)

    def __str__(self):
        return self.tag
