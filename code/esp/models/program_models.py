"""
Models that are relevant to creating and managing programs and courses.
TODO separate these models into different categories? e.g. program-relevant, course-relevant
"""

from collections import defaultdict

from django.core.validators import RegexValidator
from django.db import models
from django.db.models import Max, Min
from django.utils import timezone

from common.constants import GradeLevel, UserType, Weekday
from common.models import BaseModel
from esp.constants import (
    ClassroomTagCategory,
    CourseDifficulty,
    CourseStatus,
    FormIntegration,
    ProgramTagCategory,
    ProgramType,
    StudentRegistrationStepType,
    TeacherRegistrationStepType,
)


class ProgramConfiguration(BaseModel):
    """ProgramConfiguration represents a set of configuration for programs, e.g. stages and registration steps."""

    saved_as_preset = models.BooleanField(default=False)
    name = models.CharField(max_length=512, null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name


class CourseCategory(BaseModel):
    """
    Generally speaking, the category of class (art, science, math, CS, ...).
    This should be viewable by everyone and editable by teachers.
    """

    display_name = models.CharField(
        max_length=256, null=True, blank=True
    )  #: name of category
    symbol = models.CharField(
        max_length=1,
        null=True,
        validators=[RegexValidator(r"^[A-Za-z]{1}", "Must be a single letter.")],
    )  #: single-letter abbreviation (e.g. math = M)
    current = models.BooleanField(
        default=True
    )  #: whether this course category is currently in use

    def __str__(self):
        return self.symbol

    class Meta(BaseModel.Meta):
        verbose_name_plural = "Course categories"


class CourseFlag(BaseModel):
    """
    Flags that ESP admins use to indicate information about a course
    (e.g. review stage, needs director review, specific classroom requests)
    """

    display_name = models.CharField(max_length=256, null=True, blank=True)
    show_in_dashboard = models.BooleanField(default=True)
    show_in_scheduler = models.BooleanField(default=True)

    def __str__(self):
        return self.display_name


class Program(BaseModel):
    """An ESP program instance, e.g. Splash 2021"""

    program_configuration = models.ForeignKey(
        ProgramConfiguration, on_delete=models.PROTECT, related_name="+", null=True
    )
    name = models.CharField(max_length=512)
    program_type = models.CharField(
        choices=ProgramType.choices, max_length=128, null=True, blank=True
    )  #: type of program (e.g. Splash, Spark, ...)
    min_grade_level = models.IntegerField(choices=GradeLevel.choices, default=7)
    max_grade_level = models.IntegerField(choices=GradeLevel.choices, default=12)
    description = models.TextField(null=True)
    notes = models.TextField(null=True, blank=True)

    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    number_of_weeks = models.IntegerField()
    time_block_minutes = models.IntegerField(
        default=30
    )  #: duration of each course time block

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
            < self.teacher_registration_steps.aggregate(start=Min("access_start_date"))[
                "start"
            ]
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

    program = models.ForeignKey(
        Program, related_name="courses", on_delete=models.PROTECT
    )  #: program in which this course is offered
    name = models.CharField(
        max_length=2048, verbose_name="Class title"
    )  #: course title
    display_id = models.BigIntegerField(
        null=True, blank=True
    )  #: unique ID for this course; should be automatically generated
    # start_date = models.DateTimeField(null=True, blank=True)
    # end_date = models.DateTimeField(null=True, blank=True)
    category = models.ForeignKey(
        CourseCategory, related_name="category", on_delete=models.PROTECT, null=True
    )  #: subject area of this course (e.g. CS, science, arts, ...)
    description = models.TextField(
        help_text="A description of the class that will be shown to students."
    )  #: publicly visible course description

    max_section_size = models.IntegerField(
        verbose_name="How many students can a single section include?"
    )  #: capacity for one section of this course
    max_sections = models.IntegerField(
        default=1, verbose_name="How many enrollment sections are you willing to teach?"
    )  #: maximum number of sections for this course that could be taught
    time_slots_per_session = models.IntegerField(
        default=2,
        verbose_name="How many time slots is each session of the class?",
    )  #: number of time slots one section takes (i.e. how long)
    number_of_weeks = models.IntegerField(
        default=1, verbose_name="How many weeks will this class last?"
    )  #: number of weeks this class will last. This may be relevant to HSSPs (as of 11/2022)
    sessions_per_week = models.IntegerField(
        default=1,
        verbose_name="How often will this class meet per week?",
        help_text="If you would like to meet multiple times per week, please describe why in the comments.",
    )  #: number of times a section of this course meets per week

    prerequisites = models.TextField(
        default="None",
        blank=True,
        help_text="Describe the recommended prerequisites for this class.",
    )  #: prerequisites for taking this course, if any
    min_grade_level = models.IntegerField(
        choices=GradeLevel.choices, default=GradeLevel.seventh
    )  #: lowest eligible grade level for this course
    max_grade_level = models.IntegerField(
        choices=GradeLevel.choices, default=GradeLevel.twelfth
    )  #: highest eligible grade level for this course
    difficulty = models.IntegerField(
        choices=CourseDifficulty.choices, default=CourseDifficulty.easy
    )  #: difficulty rating of this course (1-4)

    status = models.CharField(
        choices=CourseStatus.choices, max_length=32, default=CourseStatus.unreviewed
    )  #: registration status of this course (e.g. accepted, unreviewed)
    teacher_notes = models.TextField(
        null=True, blank=True, help_text="Notes for admin review - leave blank if none"
    )  #: notes from teachers to admins
    admin_notes = models.TextField(null=True, blank=True)  #: notes made by admins
    flags = models.ManyToManyField(
        CourseFlag, related_name="flags", blank=True
    )  #: admin flags for this course
    planned_purchases = models.TextField(
        null=True, blank=True
    )  #: planned purchases (e.g. class supplies) for this course

    class Meta:
        unique_together = [("program_id", "display_id")]

    def get_display_name(self):
        program_type = self.program.get_program_type_display()
        program_abbreviation = (
            f"{program_type[0]}{program_type[-1]}".upper() if program_type else "ESP"
        )
        return f"{program_abbreviation}{self.display_id}: {self.name}"

    def get_next_display_id(self):
        """Generates this course's display ID, which is of the form YYYXXX in the year 2YYY."""
        base_display_id = (self.program.start_date.year % 1000) * 1000
        if not self.__class__.objects.filter(program_id=self.program_id).exists():
            return base_display_id
        return (
            self.__class__.objects.filter(program_id=self.program_id).aggregate(
                Max("display_id")
            )["display_id__max"]
            + 1
        )

    def get_teacher_names(self):
        return ", ".join(
            course_teacher.teacher_registration.user.get_full_name()
            for course_teacher in self.course_teachers.all()
        )

    def is_editable(self):
        """Returns True if this course is editable by the teachers, and False otherwise."""
        # Modify to determine teacher course editing permissions
        return self.status == CourseStatus.unreviewed

    def save(self, *args, **kwargs):
        if not self.display_id:
            self.display_id = self.get_next_display_id()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_display_name()} ({self.program})"


class TimeSlot(BaseModel):
    """
    A single time block/slot that a course can occupy.
    """

    program = models.ForeignKey(
        Program, related_name="time_slots", on_delete=models.PROTECT
    )  #: program that this timeslot belongs to
    start_datetime = models.DateTimeField()  #: starting date/time of the timeslot
    end_datetime = models.DateTimeField()  #: ending date/time of the timeslot

    def __str__(self):
        """Representative string; for use in the Django Admin Interface"""
        start = self.start_datetime.strftime("%I:%M%p").lstrip("0")
        end = self.end_datetime.strftime("%I:%M%p").lstrip("0")
        return f"{self.program.name}: {start} - {end} ({Weekday(self.start_datetime.weekday()).label})"

    def get_display_name(self):
        """Representative string; for use in a user facing context anywhere else in the codebase"""
        start = self.start_datetime.strftime("%I:%M%p").lstrip("0")
        end = self.end_datetime.strftime("%I:%M%p").lstrip("0")
        return f"{start} - {end} ({Weekday(self.start_datetime.weekday()).label})"

    class Meta(BaseModel.Meta):
        ordering = ["start_datetime"]
        unique_together = [("program_id", "start_datetime")]

    def course_teacher_availabilities(self):
        from esp.serializers import UserSerializer

        mapping = defaultdict(list)
        for teacher_availability in self.teacher_availabilities.all():
            for (
                course_teacher
            ) in teacher_availability.registration.course_teachers.all():
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
    """
    Information about a particular MIT classroom.
    """

    # TODO: add types of classrooms
    name = models.CharField(max_length=512)  #: name of the classroom
    description = models.TextField(null=True, blank=True)
    max_occupants = models.IntegerField()

    def __str__(self):
        return self.name


class ClassroomTag(BaseModel):
    """
    Tags that ESP admins use to indicate information about a classroom
    """

    # TODO remove classrooms and replace with a ForeignField within Classroom
    classrooms = models.ManyToManyField(Classroom, related_name="tags", blank=True)
    tag = models.CharField(max_length=256, unique=True)
    tag_category = models.CharField(
        choices=ClassroomTagCategory.choices,
        max_length=128,
        default=ClassroomTagCategory.other,
    )

    def __str__(self):
        return self.tag


#######################
# Program configuration
#######################


class ProgramStage(BaseModel):
    """
    ProgramStage represents configuration for a student-facing program stage, e.g. 'Initiation' or 'Post-Lottery'
    """

    program = models.ForeignKey(
        Program, related_name="stages", on_delete=models.PROTECT
    )  #: program that this ProgramStage belongs to
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
        """Returns True if this program stage is currently active, and False otherwise."""
        return self.start_date < timezone.now() < self.end_date

    def __str__(self):
        return f"{self.program}: {self.name}"


class StudentProgramRegistrationStep(BaseModel):
    """
    StudentProgramRegistrationStep represents config for a single student interaction step within a program stage.
    """

    program_stage = models.ForeignKey(
        ProgramStage, related_name="steps", on_delete=models.PROTECT
    )  #: program stage that this step is part of
    display_name = models.CharField(max_length=512, null=True, blank=True)
    step_key = models.CharField(
        choices=StudentRegistrationStepType.choices, max_length=256
    )  #: type of registration step (e.g. verify profile, lottery preferences)
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
    )  #: program to which this registration step belongs
    step_key = models.CharField(
        choices=TeacherRegistrationStepType.choices, max_length=128
    )  #: the type of program registration step
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
    """
    Forms (like waivers, medical forms) needed for programs that are hosted outside of the ESP website.
    """

    program = models.ForeignKey(
        Program, related_name="external_forms", on_delete=models.PROTECT
    )
    user_type = models.CharField(max_length=64, choices=UserType.choices)
    integration = models.CharField(
        max_length=64, choices=FormIntegration.choices
    )  #: platform this form is hosted on
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
        choices=ProgramTagCategory.choices,
        default=ProgramTagCategory.other,
        max_length=128,
    )

    def __str__(self):
        return self.tag


class PurchaseableItem(BaseModel):
    program = models.ForeignKey(
        Program, related_name="purchase_items", on_delete=models.PROTECT
    )
    item_name = models.CharField(max_length=250)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    required_for_registration = models.BooleanField(default=False)
    eligible_for_financial_aid = models.BooleanField()
    max_per_user = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.item_name} ({self.program.name})"
