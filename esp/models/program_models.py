from collections import defaultdict

from django.db import models
from django.db.models import Max, Min
from django.utils import timezone

from common.constants import GradeLevel, UserType, Weekday
from common.models import BaseModel
from esp.constants import (ClassroomTagCategory, CourseDifficulty,
                           CourseStatus, CourseTagCategory, FormIntegration,
                           ProgramTagCategory, ProgramType,
                           StudentRegistrationStepType,
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
    min_grade_level = models.IntegerField(choices=GradeLevel.choices, default=7)
    max_grade_level = models.IntegerField(choices=GradeLevel.choices, default=12)
    description = models.TextField(null=True)
    notes = models.TextField(null=True, blank=True)

    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    number_of_weeks = models.IntegerField()
    time_block_minutes = models.IntegerField(default=30)

    archive_on = models.DateTimeField(null=True)

    def show_to_students(self):
        if not self.stages.exists():
            return False
        if timezone.now() < self.stages.aggregate(Min("start_date"))["start_date__min"]:
            return False
        if self.archive_on is not None and self.archive_on < timezone.now():
            return False
        return True

    def show_to_teachers(self):
        if not self.teacher_registration_steps.exists():
            return False
        if (
            timezone.now()
            < self.teacher_registration_steps.aggregate(Min("access_start_date"))["access_start_date__min"]
        ):
            return False
        if self.archive_on is not None and self.archive_on < timezone.now():
            return False
        return True

    def show_to_volunteers(self):
        return self.archive_on is None or timezone.now() < self.archive_on

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
    max_sections = models.IntegerField(default=1, verbose_name="How many enrollment sections are you willing to teach?")
    time_slots_per_session = models.IntegerField(
        default=2, verbose_name="How many time slots is each session of the class?",
    )
    number_of_weeks = models.IntegerField(
        default=1, verbose_name="How many weeks will this class last?"
    )
    sessions_per_week = models.IntegerField(
        default=1, verbose_name="How often will this class meet per week?",
        help_text="If you would like to meet multiple times per week, please describe why in the comments."
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

    def get_display_name(self):
        program_type = self.program.get_program_type_display()
        program_abbreviation = f"{program_type[0]}{program_type[-1]}".upper() if program_type else "ESP"
        return f"{program_abbreviation}{self.display_id}: {self.name}"

    def get_next_display_id(self):
        base_display_id = (self.program.start_date.year % 1000) * 1000
        if not self.__class__.objects.filter(program_id=self.program_id).exists():
            return base_display_id
        return self.__class__.objects.filter(
            program_id=self.program_id
        ).aggregate(Max("display_id"))["display_id__max"] + 1

    def save(self, *args, **kwargs):
        if not self.display_id:
            self.display_id = self.get_next_display_id()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_display_name()} ({self.program})"


class TimeSlot(BaseModel):
    program = models.ForeignKey(Program, related_name="time_slots", on_delete=models.PROTECT)
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()

    def __str__(self):
        start = self.start_datetime.strftime('%I:%M%p').lstrip('0')
        end = self.end_datetime.strftime('%I:%M%p').lstrip('0')
        return f"{start} - {end} ({Weekday(self.start_datetime.weekday()).label})"

    class Meta(BaseModel.Meta):
        ordering = ["start_datetime"]
        unique_together = [("program_id", "start_datetime")]

    def course_teacher_availabilities(self):
        from esp.serializers import UserSerializer
        mapping = defaultdict(list)
        for teacher_availability in self.teacher_availabilities.all():
            for course_teacher in teacher_availability.registration.course_teachers.all():
                user = teacher_availability.registration.user
                if user in mapping[course_teacher.course_id]:
                    continue
                mapping[course_teacher.course_id].append(user)
        mapping_jsonable = {
            str(course_id): UserSerializer(users, many=True).data
            for course_id, users in mapping.items()
        }
        return mapping_jsonable


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

    def _get_next_or_previous_in_order(self, is_next):
        try:
            return super()._get_next_or_previous_in_order(is_next)
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

    def _get_next_or_previous_in_order(self, is_next):
        try:
            return super()._get_next_or_previous_in_order(is_next)
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
    help_text = models.TextField()
    # TODO: add support for below config
    max_count = models.IntegerField(null=True, blank=True)
    min_count = models.IntegerField(null=True, blank=True)
    has_integer_value = models.BooleanField(default=False)
    max_value = models.IntegerField(null=True, blank=True)
    min_value = models.IntegerField(null=True, blank=True)
    max_value_sum = models.IntegerField(null=True, blank=True)
    min_value_sum = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.tag


class ExternalProgramForm(BaseModel):
    program = models.ForeignKey(Program, related_name="external_forms", on_delete=models.PROTECT)
    user_type = models.CharField(max_length=64, choices=UserType.choices)
    integration = models.CharField(max_length=64, choices=FormIntegration.choices)
    integration_id = models.CharField(max_length=256, null=True, blank=True)
    url = models.URLField()
    display_name = models.CharField(max_length=256)
    required = models.BooleanField(default=True)

    def __str__(self):
        return self.display_name


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
    tag = models.CharField(max_length=256, unique=True)
    tag_category = models.CharField(
        choices=ClassroomTagCategory.choices, max_length=128, default=ClassroomTagCategory.other
    )

    def __str__(self):
        return self.tag


class PurchaseableItem(BaseModel):
    program = models.ForeignKey(Program, related_name="purchase_items", on_delete=models.PROTECT)
    item_name = models.CharField(max_length=250)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    required_for_registration = models.BooleanField(default=False)
    eligible_for_financial_aid = models.BooleanField()
    max_per_user = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.item_name} ({self.program.name})"
