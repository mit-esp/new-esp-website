import datetime
import pytz
import random

from esp.factories.program_factories import *
from esp.factories.course_scheduling_factories import *


def print_action(text):
    time = pytz.utc.localize(datetime.datetime.utcnow()).astimezone(pytz.timezone("America/New_York"))
    print(f"{time} {text}")


print_action("Creating program")
program = ProgramFactory()

print_action("Creating courses")
courses = [CourseFactory(program=program) for _ in range(random.randint(3, 12))]

print_action("Creating course sections")
course_sections = [CourseSectionFactory(course=random.choice(courses)) for _ in range(random.randint(1, 4))]

print_action("Creating time slots")
time_slot_start = datetime.datetime(2022, 1, 1, 0, 0, 0, tzinfo=pytz.UTC)
time_slot_interval = datetime.timedelta(minutes=program.time_block_minutes)
time_slots = [
    TimeSlotFactory(
        end_datetime=time_slot_start + time_slot_interval * (i + 1),
        program=program,
        start_datetime=time_slot_start + time_slot_interval * i,
    )
    for i in range(500)
]

print_action("Creating classrooms")
classrooms = [ClassroomFactory() for _ in range(random.randint(5, 20))]
classroom_time_slots = [
    ClassroomTimeSlotFactory(
        classroom=classroom,
        time_slot=time_slot,
        course_section=None,
    )
    for classroom in classrooms
    for time_slot in time_slots
    if random.random() < 0.95
]

print_action("Creating teacher registrations")
teacher_registrations = [TeacherRegistrationFactory(program=program) for _ in range(random.randint(8, 20))]

print_action("Creating course teachers and teacher availabilities")
course_teachers = []
teacher_availabilities = []
for index, teacher_registration in enumerate(teacher_registrations):
    print_action(f"Looping through {index+1} of {len(teacher_registrations)} teacher registrations")
    for course in courses:
        if random.randint(0, 10) > 1:
            continue
        course_teachers.append(CourseTeacherFactory(course=course, teacher_registration=teacher_registration))
        for time_slot in time_slots:
            if random.randint(0, 10) > 5:
                continue
            teacher_availabilities.append(TeacherAvailabilityFactory(registration=teacher_registration, time_slot=time_slot))
