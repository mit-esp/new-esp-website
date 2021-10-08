from django.urls import path

from esp.views import (AdminDashboardView, CourseCreateView, CourseListView,
                       CourseUpdateView, GuardianDashboardView,
                       PreferenceEntryView, ProgramCreateView, ProgramListView,
                       ProgramStageCreateView, ProgramStageUpdateView,
                       ProgramUpdateView, RegisterAccountView,
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

    path("programs/<uuid:pk>/registration/", PreferenceEntryView.as_view(), name="create_program_registration"),
    path('programs/<uuid:pk>/registration/continue/', PreferenceEntryView.as_view(), name="current_registration_step"),
    path('programs/<uuid:pk>/preferences/', PreferenceEntryView.as_view(), name="preference_entry")
]
