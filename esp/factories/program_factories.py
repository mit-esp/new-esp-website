"""
ESP model factories
"""
import pytz
from factory import SubFactory, Faker
from factory.django import DjangoModelFactory

from esp.models.program_models import Program, Course, TimeSlot, Classroom, ClassroomTag


class ClassroomFactory(DjangoModelFactory):
    name = Faker("bs")
    max_occupants = Faker("random_int")

    class Meta:
        model = Classroom


class ClassroomTagFactory(DjangoModelFactory):
    tag = Faker("bs")

    class Meta:
        model = ClassroomTag


class CourseFactory(DjangoModelFactory):
    program = SubFactory("esp.factories.program_factories.ProgramFactory")
    start_date = Faker("date_time", tzinfo=pytz.UTC)
    end_date = Faker("date_time", tzinfo=pytz.UTC)
    max_section_size = Faker("random_int")
    name = Faker("bs")

    class Meta:
        model = Course


class ProgramFactory(DjangoModelFactory):
    start_date = Faker("date_time", tzinfo=pytz.UTC)
    end_date = Faker("date_time", tzinfo=pytz.UTC)
    number_of_weeks = Faker("random_int")

    class Meta:
        model = Program


class TimeSlotFactory(DjangoModelFactory):
    program = SubFactory("esp.factories.program_factories.ProgramFactory")
    start_datetime = Faker("date_time", tzinfo=pytz.UTC)
    end_datetime = Faker("date_time", tzinfo=pytz.UTC)

    class Meta:
        model = TimeSlot
