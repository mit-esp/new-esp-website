from django.db import models

from common.models import BaseModel, User
from esp.constants import ProgramType, RegistrationStep


class Program(BaseModel):
    name = models.CharField(max_length=512)
    program_type = models.CharField(choices=ProgramType.choices, max_length=128, null=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    description = models.TextField(null=True)
    notes = models.TextField(null=True)


class Class(BaseModel):
    name = models.CharField(max_length=2048)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    description = models.TextField()
    notes = models.TextField()
    max_size = models.IntegerField()
    prerequisites = models.TextField()


class ProgramStage(BaseModel):
    program = models.ForeignKey(Program, related_name="stages", on_delete=models.PROTECT)
    name = models.CharField(max_length=256)
    index = models.IntegerField(default=0)
    stage_starts_on = models.DateTimeField()
    stage_ends_on = models.DateTimeField()
    description = models.TextField(default="")

    class Meta:
        constraints = [models.UniqueConstraint(fields=("program", "index"), name="unique_program_stage_index")]


class ProgramRegistrationStep(BaseModel):
    program_stage = models.ForeignKey(ProgramStage, related_name="steps", on_delete=models.PROTECT)
    display_name = models.CharField(max_length=512)
    step_key = models.CharField(choices=RegistrationStep.choices, max_length=256)
    index = models.IntegerField(default=0)
    description = models.TextField(default="")

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=("program_stage", "index"), name="unique_program_stage_step_index")
        ]


class ProgramRegistration(BaseModel):
    program = models.ForeignKey(Program, related_name="registrations", on_delete=models.PROTECT)
    program_stage = models.ForeignKey(ProgramStage, on_delete=models.PROTECT, related_name="registrations")
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="registrations")


class ProgramTag(BaseModel):
    program = models.ForeignKey(Program, on_delete=models.PROTECT, related_name="tags")
    tag = models.CharField(max_length=256)


class ClassTag(BaseModel):
    class_object = models.ForeignKey(Class, on_delete=models.PROTECT, related_name="tags")
    tag = models.CharField(max_length=256)