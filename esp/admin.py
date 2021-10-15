from django.contrib import admin

from esp.models import (course_scheduling, lottery, program,
                        student_registration)

admin.site.register(course_scheduling.ClassroomResource)
admin.site.register(course_scheduling.ResourceRequest)
admin.site.register(course_scheduling.ResourceType)
admin.site.register(lottery.PreferenceEntryCategory)
admin.site.register(lottery.PreferenceEntryConfiguration)
admin.site.register(lottery.PreferenceEntryRound)
admin.site.register(program.ClassSection)
admin.site.register(program.Classroom)
admin.site.register(program.Course)
admin.site.register(program.CourseTag)
admin.site.register(program.Program)
admin.site.register(program.ProgramStage)
admin.site.register(program.ProgramTag)
admin.site.register(program.TimeSlot)
admin.site.register(student_registration.ClassPreference)
admin.site.register(student_registration.ProgramRegistrationStep)
