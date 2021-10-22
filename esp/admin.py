from django.contrib import admin

from esp.models import course_scheduling, program, program_registration

admin.site.register(course_scheduling.ClassroomResource)
admin.site.register(course_scheduling.ResourceRequest)
admin.site.register(course_scheduling.ResourceType)
admin.site.register(program.PreferenceEntryCategory)
admin.site.register(program.ClassSection)
admin.site.register(program.Classroom)
admin.site.register(program.Course)
admin.site.register(program.CourseTag)
admin.site.register(program.ProgramRegistrationStep)
admin.site.register(program.ProgramTag)
admin.site.register(program.TimeSlot)
admin.site.register(program_registration.ClassPreference)
admin.site.register(program_registration.CompletedRegistrationStep)
admin.site.register(program_registration.StudentProfile)


class ProgramRegistrationStepInline(admin.StackedInline):
    extra = 0
    model = program.ProgramRegistrationStep


@admin.register(program.ProgramStage)
class ProgramStageAdmin(admin.ModelAdmin):
    inlines = [
        ProgramRegistrationStepInline
    ]


class ProgramStageInline(admin.StackedInline):
    extra = 0
    model = program.ProgramStage
    show_change_link = True


@admin.register(program.Program)
class ProgramAdmin(admin.ModelAdmin):
    search_fields = ("program_type", "name")
    inlines = [
        ProgramStageInline,
    ]


class PreferenceEntryCategoryInline(admin.StackedInline):
    extra = 0
    model = program.PreferenceEntryCategory


@admin.register(program.PreferenceEntryRound)
class PreferenceEntryRoundCategory(admin.ModelAdmin):
    inlines = [
        PreferenceEntryCategoryInline
    ]


class PreferenceEntryRoundInline(admin.StackedInline):
    extra = 0
    model = program.PreferenceEntryRound
    show_change_link = True


@admin.register(program.ProgramConfiguration)
class PreferenceEntryConfigurationAdmin(admin.ModelAdmin):
    inlines = [
        PreferenceEntryRoundInline,
    ]
