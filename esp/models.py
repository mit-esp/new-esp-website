from django.db import models

from common.models import BaseModel, User
from esp.constants import ProgramType, RegistrationStep


class PreferenceEntryConfiguration(BaseModel):
    saved_as_preset = models.BooleanField(default=False)
    name = models.CharField(max_length=512, null=True, blank=True)
    description = models.TextField(null=True, blank=True)


class Program(BaseModel):
    preference_entry_configuration = models.ForeignKey(
        PreferenceEntryConfiguration, on_delete=models.PROTECT, related_name="+", null=True
    )
    name = models.CharField(max_length=512)
    program_type = models.CharField(choices=ProgramType.choices, max_length=128, null=True, blank=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    description = models.TextField(null=True)
    notes = models.TextField(null=True, blank=True)


class Course(BaseModel):
    name = models.CharField(max_length=2048)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    description = models.TextField()
    notes = models.TextField()
    max_size = models.IntegerField()
    prerequisites = models.TextField()


class Classroom(BaseModel):
    name = models.CharField(max_length=512)
    description = models.TextField(null=True, blank=True)
    max_occupants = models.IntegerField()


class ResourceType(BaseModel):
    name = models.CharField(max_length=512)


class ClassroomResource(BaseModel):
    classroom = models.ForeignKey(Classroom, related_name="resources", on_delete=models.CASCADE)
    resource_type = models.ForeignKey(ResourceType, related_name="classrooms", on_delete=models.PROTECT)
    quantity = models.IntegerField(null=True, blank=True)


class ResourceRequest(BaseModel):
    course = models.ForeignKey(Course, related_name="resource_requests", on_delete=models.CASCADE)
    resource_type = models.ForeignKey(ResourceType, related_name="requests", on_delete=models.PROTECT)
    quantity = models.IntegerField(null=True, blank=True)


class ClassSection(BaseModel):
    course = models.ForeignKey(Course, related_name="sections", on_delete=models.PROTECT)
    classroom = models.ForeignKey(Classroom, related_name="sections", on_delete=models.PROTECT, null=True)
    day = models.DateField(null=True)
    start_time = models.TimeField()
    end_time = models.TimeField()


class ProgramStage(BaseModel):
    program = models.ForeignKey(Program, related_name="stages", on_delete=models.PROTECT)
    name = models.CharField(max_length=256)
    index = models.IntegerField(default=0)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    description = models.TextField(null=True, blank=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=("program_id", "index"), name="unique_program_stage_index")]


class ProgramRegistrationStep(BaseModel):
    program_stage = models.ForeignKey(ProgramStage, related_name="steps", on_delete=models.PROTECT)
    display_name = models.CharField(max_length=512, null=True, blank=True)
    step_key = models.CharField(choices=RegistrationStep.choices, max_length=256)
    index = models.IntegerField(default=0)
    description = models.TextField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=("program_stage_id", "index"), name="unique_program_stage_step_index")
        ]


class ProgramRegistration(BaseModel):
    program = models.ForeignKey(Program, related_name="registrations", on_delete=models.PROTECT)
    program_stage = models.ForeignKey(ProgramStage, on_delete=models.PROTECT, related_name="registrations")
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="registrations")


class PreferenceEntryRound(BaseModel):
    preference_entry_configuration = models.ForeignKey(
        PreferenceEntryConfiguration, on_delete=models.PROTECT, related_name="rounds"
    )
    index = models.IntegerField(default=0)
    help_text = models.TextField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=("preference_entry_configuration_id", "index"), name="unique_preference_entry_round_index"
            )
        ]


class PreferenceEntryCategory(BaseModel):
    preference_entry_round = models.ForeignKey(
        PreferenceEntryRound, related_name="categories", on_delete=models.PROTECT
    )
    tag = models.CharField(max_length=512)
    has_integer_value = models.BooleanField(default=False)
    max_value = models.IntegerField(null=True, blank=True)
    max_value_sum = models.IntegerField(null=True, blank=True)
    help_text = models.TextField()


class ClassPreference(BaseModel):
    registration = models.ForeignKey(ProgramRegistration, related_name="preferences", on_delete=models.PROTECT)
    class_section = models.ForeignKey(ClassSection, related_name="preferences", on_delete=models.PROTECT)
    category = models.ForeignKey(PreferenceEntryCategory, related_name="preferences", on_delete=models.PROTECT)
    value = models.IntegerField(null=True)


class ProgramTag(BaseModel):
    program = models.ForeignKey(Program, on_delete=models.PROTECT, related_name="tags")
    tag = models.CharField(max_length=256)


class ClassTag(BaseModel):
    course = models.ForeignKey(Course, on_delete=models.PROTECT, related_name="tags")
    tag = models.CharField(max_length=256)
