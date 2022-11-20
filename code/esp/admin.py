from django.contrib import admin

from esp.models import (course_scheduling_models, program_models,
                        program_registration_models)

admin.site.site_header = 'MIT ESP Database Administration'
admin.site.register(course_scheduling_models.CourseSection)
admin.site.register(course_scheduling_models.ClassroomTimeSlot)
# admin.site.register(course_scheduling_models.ClassroomConstraint)
admin.site.register(program_models.Classroom)
admin.site.register(program_models.ClassroomTag)
admin.site.register(program_models.CourseCategory)
admin.site.register(program_models.CourseFlag)
admin.site.register(program_models.PreferenceEntryCategory)
admin.site.register(program_models.PurchaseableItem)
admin.site.register(program_registration_models.ProgramRegistration)
admin.site.register(program_models.ProgramRegistrationStep)
admin.site.register(program_models.ProgramTag)
admin.site.register(program_models.TeacherProgramRegistrationStep)
admin.site.register(program_models.TimeSlot)
admin.site.register(program_models.ExternalProgramForm)
admin.site.register(program_registration_models.ClassPreference)
admin.site.register(program_registration_models.CompletedRegistrationStep)
admin.site.register(program_registration_models.StudentProfile)
admin.site.register(program_registration_models.TeacherProfile)


class ProgramRegistrationStepInline(admin.StackedInline):
    extra = 0
    model = program_models.ProgramRegistrationStep


@admin.register(program_models.ProgramStage)
class ProgramStageAdmin(admin.ModelAdmin):
    inlines = [
        ProgramRegistrationStepInline
    ]


class ProgramStageInline(admin.StackedInline):
    extra = 0
    model = program_models.ProgramStage
    show_change_link = True


class TeacherRegistrationStepInline(admin.StackedInline):
    extra = 0
    model = program_models.TeacherProgramRegistrationStep
    show_change_link = True


class TimeSlotInline(admin.TabularInline):
    extra = 0
    model = program_models.TimeSlot
    show_change_link = True


class ExternalProgramFormInline(admin.TabularInline):
    extra = 0
    model = program_models.ExternalProgramForm
    show_change_link = True


@admin.register(program_models.Program)
class ProgramAdmin(admin.ModelAdmin):
    search_fields = ("program_models_type", "name")
    inlines = [
        ProgramStageInline,
        TeacherRegistrationStepInline,
        TimeSlotInline,
        ExternalProgramFormInline,
    ]


class PreferenceEntryCategoryInline(admin.StackedInline):
    extra = 0
    model = program_models.PreferenceEntryCategory


@admin.register(program_models.PreferenceEntryRound)
class PreferenceEntryRoundCategory(admin.ModelAdmin):
    inlines = [
        PreferenceEntryCategoryInline
    ]


class PreferenceEntryRoundInline(admin.StackedInline):
    extra = 0
    model = program_models.PreferenceEntryRound
    show_change_link = True


@admin.register(program_models.ProgramConfiguration)
class PreferenceEntryConfigurationAdmin(admin.ModelAdmin):
    inlines = [
        PreferenceEntryRoundInline,
    ]


class CourseCategoryInline(admin.TabularInline):
    model = program_models.CourseCategory.courses.through
    extra = 0


@admin.register(program_models.Course)
class CourseAdmin(admin.ModelAdmin):
    inlines = [CourseCategoryInline]
