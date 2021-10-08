from django.contrib import admin

from esp import models

admin.site.register(models.ClassPreference)
admin.site.register(models.ClassSection)
admin.site.register(models.Classroom)
admin.site.register(models.ClassroomResource)
admin.site.register(models.Course)
admin.site.register(models.CourseTag)
admin.site.register(models.PreferenceEntryCategory)
admin.site.register(models.PreferenceEntryConfiguration)
admin.site.register(models.PreferenceEntryRound)
admin.site.register(models.Program)
admin.site.register(models.ProgramRegistrationStep)
admin.site.register(models.ProgramStage)
admin.site.register(models.ProgramTag)
admin.site.register(models.ResourceRequest)
admin.site.register(models.ResourceType)
admin.site.register(models.TimeSlot)
admin.site.register(models.User)
