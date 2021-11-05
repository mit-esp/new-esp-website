"""
ESP model factories
"""
from factory import SubFactory, Faker
from factory.django import DjangoModelFactory

from esp.models.course_scheduling import ClassroomTimeSlot, CourseSection, ClassroomConstraint


class ClassroomConstraintFactory(DjangoModelFactory):
    course = SubFactory("esp.factories.program_factories.CourseFactory")
    required_classroom_tag = SubFactory("esp.factories.program_factories.ClassroomTagFactory")
    constraint = Faker("bs")

    class Meta:
        model = ClassroomConstraint


class ClassroomTimeSlotFactory(DjangoModelFactory):
    classroom = SubFactory("esp.factories.program_factories.ClassroomFactory")
    time_slot = SubFactory("esp.factories.program_factories.TimeSlotFactory")
    course_section = SubFactory("esp.factories.course_scheduling_factories.CourseSectionFactory")

    class Meta:
        model = ClassroomTimeSlot


class CourseSectionFactory(DjangoModelFactory):
    course = SubFactory("esp.factories.program_factories.CourseFactory")

    class Meta:
        model = CourseSection
