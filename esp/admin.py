from django.contrib import admin

from esp.models import course_scheduling, program, program_registration

admin.site.register(course_scheduling.CourseSection)
admin.site.register(course_scheduling.ClassroomTimeSlot)
# admin.site.register(course_scheduling.ClassroomConstraint)
admin.site.register(program.Classroom)
admin.site.register(program.CourseTag)
admin.site.register(program.PreferenceEntryCategory)
admin.site.register(program.ProgramRegistrationStep)
admin.site.register(program.ProgramTag)
admin.site.register(program.TeacherProgramRegistrationStep)
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


class TeacherRegistrationStepInline(admin.StackedInline):
    extra = 0
    model = program.TeacherProgramRegistrationStep
    show_change_link = True


class TimeSlotInline(admin.TabularInline):
    extra = 0
    model = program.TimeSlot
    show_change_link = True


@admin.register(program.Program)
class ProgramAdmin(admin.ModelAdmin):
    search_fields = ("program_type", "name")
    inlines = [
        ProgramStageInline,
        TeacherRegistrationStepInline,
        TimeSlotInline,
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


class CourseTagInline(admin.TabularInline):
    model = program.CourseTag.courses.through
    extra = 0


@admin.register(program.Course)
class CourseAdmin(admin.ModelAdmin):
    inlines = [CourseTagInline]
