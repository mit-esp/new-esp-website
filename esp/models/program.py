from django.db import models
from django.db.models import Max, Min
from django.utils import timezone

from common.constants import GradeLevel, Weekday
from common.models import BaseModel
from esp.constants import (ClassroomTagCategory, CourseDifficulty,
                           CourseStatus, CourseTagCategory, ProgramTagCategory,
                           ProgramType, StudentRegistrationStepType,
                           TeacherRegistrationStepType)


class ProgramConfiguration(BaseModel):
    """ProgramConfiguration represents a set of configuration for programs, e.g. stages and registration steps."""
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

    archive_on = models.DateTimeField()

    def show_to_students(self):
        if not self.stages.exists():
            return False
        return (
                self.stages.aggregate(Min("start_date"))["start_date__min"]
                < timezone.now()
                < self.archive_on
        )

    def show_to_teachers(self):
        if not self.teacher_registration_steps.exists():
            return False
        return (
            self.teacher_registration_steps.aggregate(Min("access_start_date"))["access_start_date__min"]
            < timezone.now()
            < self.archive_on
        )

    def show_to_volunteers(self):
        return timezone.now() < self.archive_on

    def __str__(self):
        return self.name


class Course(BaseModel):
    """
    Course represents an ESP class in a specific program (named to avoid reserved word 'class' conflicts).
    It is still referred to as 'class' in urls and on the frontend to match existing terminology.
    """
    program = models.ForeignKey(Program, related_name="courses", on_delete=models.PROTECT)
    name = models.CharField(max_length=2048, verbose_name="Class title")
    display_id = models.BigIntegerField(null=True, blank=True)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    description = models.TextField(help_text="A description of the class that will be shown to students.")
    max_section_size = models.IntegerField(verbose_name="How many students can a single section include?")
    max_sections = models.IntegerField(verbose_name="How many sections are you willing to teach?")
    duration_minutes = models.IntegerField(
        default=60, verbose_name="How long (in minutes) should this class be?",
        help_text="We will attempt to accommodate this within the constraints of the program time blocks."
    )
    prerequisites = models.TextField(
        default="None", blank=True, help_text="Describe the recommended prerequisites for this class."
    )
    min_grade_level = models.IntegerField(choices=GradeLevel.choices, default=GradeLevel.seventh)
    max_grade_level = models.IntegerField(choices=GradeLevel.choices, default=GradeLevel.twelfth)
    difficulty = models.IntegerField(choices=CourseDifficulty.choices, default=CourseDifficulty.easy)

    status = models.CharField(choices=CourseStatus.choices, max_length=32, default=CourseStatus.unreviewed)
    teacher_notes = models.TextField(null=True, blank=True, help_text="Notes for admin review - leave blank if none")
    admin_notes = models.TextField(null=True, blank=True)
    planned_purchases = models.TextField(null=True, blank=True)

    class Meta:
        unique_together = [("program_id", "display_id")]

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


class Classroom(BaseModel):
    name = models.CharField(max_length=512)
    description = models.TextField(null=True, blank=True)
    max_occupants = models.IntegerField()

    def __str__(self):
        return self.name


#######################
# Program configuration
#######################

class ProgramStage(BaseModel):
    """ProgramStage represents configuration for a student-facing program stage, e.g. 'Initiation' or 'Post-Lottery'"""
    program = models.ForeignKey(Program, related_name="stages", on_delete=models.PROTECT)
    name = models.CharField(max_length=256)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    description = models.TextField(null=True, blank=True)

    class Meta(BaseModel.Meta):
        order_with_respect_to = "program"

    def get_next_in_order(self):
        try:
            return super().get_next_in_order()
        except self.DoesNotExist:
            return None

    def get_previous_in_order(self):
        try:
            return super().get_previous_in_order()
        except self.DoesNotExist:
            return None

    def is_active(self):
        return self.start_date < timezone.now() < self.end_date

    def __str__(self):
        return f"{self.program}: {self.name}"


class ProgramRegistrationStep(BaseModel):
    """ProgramRegistrationStep represents config for a single student interaction step within a program stage."""
    program_stage = models.ForeignKey(ProgramStage, related_name="steps", on_delete=models.PROTECT)
    display_name = models.CharField(max_length=512, null=True, blank=True)
    step_key = models.CharField(choices=StudentRegistrationStepType.choices, max_length=256)
    required_for_stage_completion = models.BooleanField(default=True)
    display_after_completion = models.BooleanField(default=True)
    allow_changes_after_completion = models.BooleanField(default=True)
    description = models.TextField(null=True, blank=True)

    class Meta(BaseModel.Meta):
        unique_together = [("program_stage_id", "step_key")]

    def get_display_name(self):
        return self.display_name or self.get_step_key_display()

    def __str__(self):
        return f"{self.program_stage} - {self.get_display_name()}"


class TeacherProgramRegistrationStep(BaseModel):
    """
    TeacherProgramRegistrationStep represents an (ordered) step in the teacher registration process.
    Unlike student registration, teacher registration is not split into phases; instead, all active steps are displayed.
    """
    program = models.ForeignKey(
        Program, related_name="teacher_registration_steps", on_delete=models.PROTECT
    )
    step_key = models.CharField(choices=TeacherRegistrationStepType.choices, max_length=128)
    display_name = models.CharField(max_length=512, null=True, blank=True)
    access_start_date = models.DateTimeField()
    access_end_date = models.DateTimeField()
    required_for_next_step = models.BooleanField(default=True)
    display_after_completion = models.BooleanField(default=True)
    allow_changes_after_completion = models.BooleanField(default=True)
    description = models.TextField(null=True, blank=True)

    class Meta(BaseModel.Meta):
        unique_together = [("program_id", "step_key")]
        order_with_respect_to = "program"

    def get_next_in_order(self):
        try:
            return super().get_next_in_order()
        except self.DoesNotExist:
            return None

    def get_previous_in_order(self):
        try:
            return super().get_previous_in_order()
        except self.DoesNotExist:
            return None

    def get_display_name(self):
        return self.display_name or self.get_step_key_display()

    def __str__(self):
        return f"{self.program} - {self.get_display_name()}"


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

    def _get_next_or_previous_in_order(self, is_next):
        try:
            return super()._get_next_or_previous_in_order(is_next)
        except self.DoesNotExist:
            return None

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


class ProgramTag(BaseModel):
    programs = models.ManyToManyField(Program, related_name="tags", blank=True)
    tag = models.CharField(max_length=256)
    tag_category = models.CharField(
        choices=ProgramTagCategory.choices, default=ProgramTagCategory.other, max_length=128
    )

    def __str__(self):
        return self.tag


class CourseTag(BaseModel):
    courses = models.ManyToManyField(Course, related_name="tags", blank=True)
    tag = models.CharField(max_length=256)
    display_name = models.CharField(max_length=256, null=True, blank=True)
    tag_category = models.CharField(choices=CourseTagCategory.choices, default=CourseTagCategory.other, max_length=128)
    editable_by_teachers = models.BooleanField()
    viewable_by_teachers = models.BooleanField()
    viewable_by_students = models.BooleanField()

    def __str__(self):
        return self.tag


class ClassroomTag(BaseModel):
    classrooms = models.ManyToManyField(Classroom, related_name="tags", blank=True)
    tag = models.CharField(max_length=256)
    tag_category = models.CharField(
        choices=ClassroomTagCategory.choices, max_length=128, default=ClassroomTagCategory.other
    )

    def __str__(self):
        return self.tag
