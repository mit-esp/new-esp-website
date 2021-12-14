import datetime
import random

from esp.factories.program_factories import *
from esp.factories.course_scheduling_factories import *


program = ProgramFactory()
courses = [CourseFactory(program=program) for _ in range(random.randint(3, 12))]
course_sections = [CourseSectionFactory(course=random.choice(courses)) for _ in range(random.randint(1, 4))]
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
