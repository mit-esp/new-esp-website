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
                       RegistrationStepPlaceholderView, StudentDashboardView,
                       StudentProfileCreateView, StudentProfileUpdateView,
                       TeacherDashboardView, VolunteerDashboardView)

urlpatterns = [
    # User setup
    path('accounts/register', RegisterAccountView.as_view(), name="register_account"),
    path('accounts/student/', StudentProfileCreateView.as_view(), name="create_student_profile"),
    path('accounts/student/update/<uuid:pk>/', StudentProfileUpdateView.as_view(), name="update_student_profile"),

    # Dashboards
    path('dashboard/admin/', AdminDashboardView.as_view(), name="admin_dashboard"),
    path('dashboard/guardian/', GuardianDashboardView.as_view(), name="guardian_dashboard"),
    path('dashboard/student/', StudentDashboardView.as_view(), name="student_dashboard"),
    path('dashboard/teacher/', TeacherDashboardView.as_view(), name="teacher_dashboard"),
    path('dashboard/volunteer/', VolunteerDashboardView.as_view(), name="volunteer_dashboard"),

    # Admin views
    path('admin/programs/create/', ProgramCreateView.as_view(), name='create_program'),
    path('admin/programs/update/<uuid:pk>/', ProgramUpdateView.as_view(), name='update_program'),
    path('admin/programs/<uuid:pk>/stages/create/', ProgramStageCreateView.as_view(), name="create_program_stage"),
    path('admin/programs/<uuid:pk>/stages/update/', ProgramStageUpdateView.as_view(), name="update_program_stage"),
    path('admin/programs/all/', ProgramListView.as_view(), name='programs'),

    path('admin/classes/create/', CourseCreateView.as_view(), name='create_course'),
    path('admin/classes/update/<uuid:pk>/', CourseUpdateView.as_view(), name='update_course'),
    path('admin/classes/all/', CourseListView.as_view(), name='courses'),

    # Program registration views
    path(
        "programs/<uuid:pk>/registration/", ProgramRegistrationCreateView.as_view(), name="create_program_registration"
    ),
    path(
        'programs/registration/<uuid:pk>/continue/', ProgramRegistrationStageView.as_view(),
        name="current_registration_stage"
    ),

    # Registration step initial views
    # Each registration step in esp.constants.RegistrationStep must have a corresponding view with a url name that
    #   matches the choice name, and which must take registration_id and step_id parameters.
    # This view is responsible for initiating the registration step and will be linked to in any registration
    #   stage that includes that step.
    path(
        'programs/registration/<uuid:registration_id>/verify_profile/<uuid:step_id>/',
        RegistrationStepPlaceholderView.as_view(), name=RegistrationStep.verify_profile
    ),
    path(
        'programs/registration/<uuid:registration_id>/waivers/<uuid:step_id>/',
        RegistrationStepPlaceholderView.as_view(), name=RegistrationStep.submit_waivers
    ),
    path(
        'programs/registration/<uuid:registration_id>/availability/<uuid:step_id>/',
        RegistrationStepPlaceholderView.as_view(), name=RegistrationStep.time_availability
    ),
    path(
        'programs/registration/<uuid:registration_id>/preferences/<uuid:step_id>/',
        InitiatePreferenceEntryView.as_view(), name=RegistrationStep.lottery_preferences
    ),
    path(
        'programs/registration/<uuid:registration_id>/submit/<uuid:step_id>/',
        RegistrationStepPlaceholderView.as_view(), name=RegistrationStep.submit_registration
    ),
    path(
        'programs/registration/<uuid:registration_id>/lottery_results/<uuid:step_id>/',
        RegistrationStepPlaceholderView.as_view(), name=RegistrationStep.view_assigned_courses
    ),
    path(
        'programs/registration/<uuid:registration_id>/edit_classes/<uuid:step_id>/',
        RegistrationStepPlaceholderView.as_view(), name=RegistrationStep.edit_assigned_courses
    ),
    path(
        'programs/registration/<uuid:registration_id>/fees/<uuid:step_id>/',
        RegistrationStepPlaceholderView.as_view(), name=RegistrationStep.pay_program_fees
    ),
    path(
        'programs/registration/<uuid:registration_id>/check_in/<uuid:step_id>/',
        RegistrationStepPlaceholderView.as_view(), name=RegistrationStep.check_in
    ),
    path(
        'programs/registration/<uuid:registration_id>/surveys/<uuid:step_id>/',
        RegistrationStepPlaceholderView.as_view(), name=RegistrationStep.complete_surveys
    ),

    # Registration step additional views
    # Preference entry views
    path(
        'programs/registration/<uuid:registration_id>/preferences/<uuid:step_id>/round_<int:index>/',
        PreferenceEntryRoundView.as_view(), name="preference_entry_round"),
    path(
        'programs/registration/<uuid:registration_id>/step/<uuid:step_id>/complete/',
        RegistrationStepCompleteView.as_view(), name="complete_registration_step",
    )
]
