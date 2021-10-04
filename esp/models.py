from django.db import models

from common.models import BaseModel


class Program(BaseModel):
    name = models.CharField(max_length=512)
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
