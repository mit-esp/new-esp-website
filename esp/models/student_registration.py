from django.db import models

from common.constants import USStateEquiv
from common.models import BaseModel, User
from esp.constants import HeardAboutVia, RegistrationStep
from esp.models.preference_matching import PreferenceEntryCategory
from esp.models.program import ClassSection, Program, ProgramStage


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


class ClassPreference(BaseModel):
    """ClassPreference represents a preference entry category that a user has applied to a class section."""
    registration = models.ForeignKey(ProgramRegistration, related_name="preferences", on_delete=models.PROTECT)
    class_section = models.ForeignKey(ClassSection, related_name="preferences", on_delete=models.PROTECT)
    category = models.ForeignKey(PreferenceEntryCategory, related_name="preferences", on_delete=models.PROTECT)

    def __str__(self):
        return f"{self.registration} - {self.category} preference"


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
