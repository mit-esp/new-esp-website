from django.db import models
from django.db.models import Max
from django.utils import timezone

from common.constants import GradeLevel, USStateEquiv, Weekday
from common.models import BaseModel, User
from esp.constants import (CourseDifficulty, CourseRoleType, CourseStatus,
                           HeardAboutVia, ProgramType, RegistrationStep)


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
    min_grade_level = models.IntegerField(choices=GradeLevel.choices, default=7)
    max_grade_level = models.IntegerField(choices=GradeLevel.choices, default=12)
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
    day = models.IntegerField(choices=Weekday.choices, null=True, blank=True)
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        start = self.start_time.strftime('%I:%M%p').lstrip('0')
        end = self.end_time.strftime('%I:%M%p').lstrip('0')
        return f"{start} - {end}" + (f" ({self.get_day_display()})" if self.day else "")

    class Meta(BaseModel.Meta):
        ordering = ("day", "start_time")


class ClassroomAvailability(BaseModel):
    classroom = models.ForeignKey(Classroom, related_name="time_slots", on_delete=models.CASCADE)
    time_slot = models.ForeignKey(TimeSlot, related_name="classrooms", on_delete=models.PROTECT)


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

    def show_on_dashboard(self):
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


class ProgramRegistration(BaseModel):
    """ProgramRegistration represents a user's registration for a program."""
    program = models.ForeignKey(Program, related_name="registrations", on_delete=models.PROTECT)
    program_stage = models.ForeignKey(ProgramStage, on_delete=models.PROTECT, related_name="registrations")
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="registrations")

    def __str__(self):
        return f"{self.program} registration for {self.user}"


class CompletedRegistrationStep(BaseModel):
    registration = models.ForeignKey(ProgramRegistration, related_name="completed_steps", on_delete=models.PROTECT)
    step = models.ForeignKey(ProgramRegistrationStep, related_name="registrations", on_delete=models.PROTECT)


class PreferenceEntryRound(BaseModel):
    preference_entry_configuration = models.ForeignKey(
        PreferenceEntryConfiguration, on_delete=models.PROTECT, related_name="rounds"
    )
    title = models.CharField(max_length=512, null=True, blank=True)
    help_text = models.TextField()
    group_sections_by_course = models.BooleanField(default=False)
    applied_category_filter = models.CharField(max_length=512, null=True, blank=True)

    class Meta(BaseModel.Meta):
        order_with_respect_to = "preference_entry_configuration_id"

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


class ClassPreference(BaseModel):
    """ClassPreference represents a preference entry category that a user has applied to a class section."""
    registration = models.ForeignKey(ProgramRegistration, related_name="preferences", on_delete=models.PROTECT)
    class_section = models.ForeignKey(ClassSection, related_name="preferences", on_delete=models.PROTECT)
    category = models.ForeignKey(PreferenceEntryCategory, related_name="preferences", on_delete=models.PROTECT)

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


class StudentProfile(BaseModel):
    user = models.OneToOneField(User, on_delete=models.PROTECT, related_name="student_profile")
    address_street = models.CharField(max_length=512)
    address_city = models.CharField(max_length=512)
    address_state = models.CharField(choices=USStateEquiv.choices, max_length=16)
    address_zip = models.CharField(max_length=10)

    home_phone = models.CharField(max_length=16)
    cell_phone = models.CharField(max_length=16, null=True, blank=True)

    dob = models.DateField()
    graduation_year = models.CharField(max_length=4)
    school = models.CharField(max_length=512)
    heard_about_esp_via = models.CharField(
        choices=HeardAboutVia.choices, max_length=32, verbose_name="How did you hear about this program?",
        help_text="If you select 'Other', please provide detail in the text box."
    )
    heard_about_esp_other_detail = models.CharField(max_length=1024, null=True, blank=True)

    guardian_first_name = models.CharField(max_length=128)
    guardian_last_name = models.CharField(max_length=128)
    guardian_email = models.EmailField()
    guardian_home_phone = models.CharField(max_length=16)
    guardian_cell_phone = models.CharField(max_length=16, null=True, blank=True)

    emergency_contact_first_name = models.CharField(max_length=128)
    emergency_contact_last_name = models.CharField(max_length=128)
    emergency_contact_email = models.EmailField()
    emergency_contact_address_street = models.CharField(max_length=512)
    emergency_contact_address_city = models.CharField(max_length=512)
    emergency_contact_address_state = models.CharField(choices=USStateEquiv.choices, max_length=16)
    emergency_contact_address_zip = models.CharField(max_length=10)
    emergency_contact_home_phone = models.CharField(max_length=16)
    emergency_contact_cell_phone = models.CharField(max_length=16, null=True, blank=True)
