from datetime import date

from django.db import models
from django.db.models import Exists, OuterRef, Q
from django.db.models.functions import Now
from django.utils import timezone

from common.constants import GradeLevel, ShirtSize, USStateEquiv
from common.models import BaseModel, User
from esp.constants import HeardAboutVia, MITAffiliation, RegistrationStep
from esp.models.program import (ClassSection, Course, PreferenceEntryCategory,
                                Program, ProgramRegistrationStep, TimeSlot)

#######################
# Student Registrations
#######################


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

    def grade_level(self):
        current_date = timezone.now().date()
        # Assumes graduation on July 1
        years_until_graduation = int((date(year=int(self.graduation_year), month=7, day=1) - current_date).days/365)
        return 12 - years_until_graduation

    def get_grade_level_display(self):
        grade_level = self.grade_level()
        if grade_level > 12:
            return "Graduated"
        return GradeLevel(grade_level).label


class ProgramRegistration(BaseModel):
    """ProgramRegistration represents a user's registration for a program."""
    program = models.ForeignKey(Program, related_name="registrations", on_delete=models.PROTECT)
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="registrations")

    def get_program_stage(self):
        active_stages = self.program.stages.filter(
            Q(start_date__lte=Now(), end_date__gte=Now(), manually_hidden=False) | Q(manually_activated=True)
        )
        completed_steps = self.completed_steps.values_list("step_id", flat=True)
        incomplete_stages = active_stages.filter(
            Exists(RegistrationStep.objects
                   .filter(program_stage_id=OuterRef('id'), required_for_stage_completion=True)
                   .exclude(steps__id__in=completed_steps))
        )
        if incomplete_stages:
            return incomplete_stages.first()
        return active_stages.last()

    def __str__(self):
        return f"{self.program} registration for {self.user}"


class CompletedRegistrationStep(BaseModel):
    registration = models.ForeignKey(ProgramRegistration, related_name="completed_steps", on_delete=models.PROTECT)
    step = models.ForeignKey(ProgramRegistrationStep, related_name="registrations", on_delete=models.PROTECT)
    completed_on = models.DateTimeField()


class StudentAvailability(BaseModel):
    registration = models.ForeignKey(ProgramRegistration, related_name="availabilities", on_delete=models.PROTECT)
    time_slot = models.ForeignKey(TimeSlot, related_name="student_availabilities", on_delete=models.PROTECT)


class ClassPreference(BaseModel):
    """ClassPreference represents a preference entry category that a user has applied to a class section."""
    registration = models.ForeignKey(ProgramRegistration, related_name="preferences", on_delete=models.PROTECT)
    class_section = models.ForeignKey(ClassSection, related_name="preferences", on_delete=models.PROTECT)
    category = models.ForeignKey(PreferenceEntryCategory, related_name="preferences", on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.registration} - {self.category} preference"


class ClassRegistration(BaseModel):
    class_section = models.ForeignKey(ClassSection, related_name="registrations", on_delete=models.PROTECT)
    program_registration = models.ForeignKey(
        ProgramRegistration, related_name="class_registrations", on_delete=models.PROTECT
    )
    created_by_lottery = models.BooleanField()
    confirmed_on = models.DateTimeField(null=True)

#######################
# Teacher Registrations
#######################


class TeacherProfile(BaseModel):
    user = models.OneToOneField(User, related_name="teacher_profile", on_delete=models.PROTECT)
    mit_affiliation = models.CharField(
        choices=MITAffiliation.choices, max_length=32, verbose_name="What is your affiliation with MIT?"
    )
    major = models.CharField(
        max_length=128, blank=True, null=True,
        help_text="If you are currently a student, please provide your major or degree field."
    )
    graduation_year = models.CharField(
        max_length=4, blank=True, null=True,
        help_text="If you are currently a student, please provide your graduation year."
    )
    university_or_employer = models.CharField(
        max_length=128, blank=True, null=True,
        help_text="If you are not affiliated with MIT, please provide your university or employer."
    )
    bio = models.TextField(blank=True, null=True)
    shirt_size = models.CharField(max_length=3, choices=ShirtSize.choices)


class TeacherRegistration(BaseModel):
    program = models.ForeignKey(Program, related_name="teacher_registrations", on_delete=models.PROTECT)
    user = models.ForeignKey(User, related_name="teacher_registrations", on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.program} registration for {self.user}"


class CourseTeacher(BaseModel):
    course = models.ForeignKey(Course, related_name="teachers", on_delete=models.PROTECT)
    teacher_registration = models.ForeignKey(TeacherRegistration, related_name="courses", on_delete=models.PROTECT)


class TeacherAvailability(BaseModel):
    registration = models.ForeignKey(TeacherRegistration, related_name="availabilities", on_delete=models.PROTECT)
    time_slot = models.ForeignKey(TimeSlot, related_name="teacher_availabilities", on_delete=models.PROTECT)
