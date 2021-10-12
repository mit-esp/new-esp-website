from django.urls import path

from esp.constants import RegistrationStep
from esp.views import (AdminDashboardView, CourseCreateView, CourseListView,
                       CourseUpdateView, GuardianDashboardView,
                       InitiatePreferenceEntryView, PreferenceEntryRoundView,
                       ProgramCreateView, ProgramListView,
                       ProgramRegistrationCreateView,
                       ProgramRegistrationStageView, ProgramStageCreateView,
                       ProgramStageUpdateView, ProgramUpdateView,
                       RegisterAccountView, RegistrationStepCompleteView,
                       StudentDashboardView, TeacherDashboardView)

urlpatterns = [
    path('accounts/register', RegisterAccountView.as_view(), name="register_account"),

    path('programs/create/', ProgramCreateView.as_view(), name='create_program'),
    path('programs/update/<uuid:pk>/', ProgramUpdateView.as_view(), name='update_program'),
    path('programs/<uuid:pk>/stages/create/', ProgramStageCreateView.as_view(), name="create_program_stage"),
    path('programs/<uuid:pk>/stages/update/', ProgramStageUpdateView.as_view(), name="update_program_stage"),
    path('programs/all/', ProgramListView.as_view(), name='programs'),

    path('classes/create/', CourseCreateView.as_view(), name='create_course'),
    path('classes/update/<uuid:pk>/', CourseUpdateView.as_view(), name='update_course'),
    path('classes/all/', CourseListView.as_view(), name='courses'),

    path('dashboard/admin/', AdminDashboardView.as_view(), name="admin_dashboard"),
    path('dashboard/guardian/', GuardianDashboardView.as_view(), name="guardian_dashboard"),
    path('dashboard/student/', StudentDashboardView.as_view(), name="student_dashboard"),
    path('dashboard/teacher/', TeacherDashboardView.as_view(), name="teacher_dashboard"),

    path(
        "programs/<uuid:pk>/registration/", ProgramRegistrationCreateView.as_view(), name="create_program_registration"
    ),
    path(
        'programs/registration/<uuid:pk>/continue/', ProgramRegistrationStageView.as_view(),
        name="current_registration_stage"
    ),
    path(
        'programs/registration/<uuid:pk>/preferences/<uuid:step_id>/', InitiatePreferenceEntryView.as_view(),
        name=RegistrationStep.lottery_preferences
    ),
    path(
        'programs/registration/<uuid:registration_id>/preferences/<uuid:step_id>/round_<int:index>/',
        PreferenceEntryRoundView.as_view(), name="preference_entry_round"),
    path(
        'programs/registration/<uuid:registration_id>/step/<uuid:step_id>/complete/',
        RegistrationStepCompleteView.as_view(), name="complete_registration_step",
    )
]
