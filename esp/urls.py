from django.urls import path

from esp.constants import StudentRegistrationStepType
from esp.views.admin_pages import (AdminDashboardView, CourseCreateView,
                                   CourseListView, CourseUpdateView,
                                   ProgramCreateView, ProgramListView,
                                   ProgramLotteryView, ProgramStageCreateView,
                                   ProgramStageUpdateView, ProgramUpdateView)
from esp.views.scheduler import (ClassroomApiView, ClassroomTimeSlotApiView,
                                 CourseApiView, CourseSectionApiView,
                                 SchedulerView, TimeSlotApiView)
from esp.views.student_registration_pages import (
    CompleteSurveysView, ConfirmAssignedCoursesView,
    ConfirmRegistrationSubmissionView, DeleteCourseRegistrationView,
    EditAssignedCoursesView, InitiatePreferenceEntryView, PayProgramFeesView,
    PreferenceEntryRoundView, ProgramRegistrationCreateView,
    ProgramRegistrationStageView, RegistrationStepCompleteView,
    StudentAvailabilityView, SubmitWaiversView, VerifyStudentProfileView)
from esp.views.teacher_registration_pages import (
    AddCoTeacherView, TeacherEditCourseView, TeacherProgramDashboardView,
    TeacherProgramRegistrationCreateView, TeacherRegistrationStepRouterView)
from esp.views.user_pages import (GuardianDashboardView, RegisterAccountView,
                                  StudentDashboardView,
                                  StudentProfileCreateView,
                                  StudentProfileUpdateView,
                                  TeacherDashboardView,
                                  TeacherProfileCreateView,
                                  TeacherProfileUpdateView,
                                  VolunteerDashboardView)

urlpatterns = [
    # User setup
    path('accounts/register/', RegisterAccountView.as_view(), name="register_account"),
    path('accounts/student/', StudentProfileCreateView.as_view(), name="create_student_profile"),
    path('accounts/student/update/<uuid:pk>/', StudentProfileUpdateView.as_view(), name="update_student_profile"),
    path('accounts/teacher/', TeacherProfileCreateView.as_view(), name="create_teacher_profile"),
    path('accounts/teacher/update/<uuid:pk>/', TeacherProfileUpdateView.as_view(), name="update_teacher_profile"),

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

    path('admin/programs/<uuid:pk>/lottery/', ProgramLotteryView.as_view(), name="program_lottery"),

    # Teacher program registration views
    path(
        "programs/<uuid:pk>/teach/register/", TeacherProgramRegistrationCreateView.as_view(),
        name="create_teacher_registration"
    ),
    path(
        "programs/teach/registration/<uuid:pk>/", TeacherProgramDashboardView.as_view(),
        name="teacher_program_dashboard",
    ),
    path(
        "programs/teach/registration/<uuid:registration_id>/<uuid:step_id>/",
        TeacherRegistrationStepRouterView.as_view(), name="teacher_registration_step"
    ),
    path("programs/courses/<uuid:pk>/edit/", TeacherEditCourseView.as_view(), name="teacher_edit_course"),
    path("programs/courses/<uuid:pk>/coteacher/", AddCoTeacherView.as_view(), name="add_coteacher"),

    # Student program registration views
    path("programs/<uuid:pk>/register/", ProgramRegistrationCreateView.as_view(), name="create_program_registration"),
    path(
        'programs/registration/<uuid:pk>/', ProgramRegistrationStageView.as_view(),
        name="current_registration_stage"
    ),
    path(
        'programs/registration/<uuid:registration_id>/edit_classes/',
        EditAssignedCoursesView.as_view(), name="edit_student_courses"
    ),
    path(
        'programs/registration/remove_class/<uuid:pk>/',
        DeleteCourseRegistrationView.as_view(), name='delete_course_registration'
    ),

    # Student registration step initial views
    # Each registration step in esp.constants.StudentRegistrationStepType must have a corresponding view with a url name
    # that matches the choice name, and which must take registration_id and step_id parameters.
    # This view is responsible for initiating the registration step and will be linked to in any registration
    #   stage that includes that step.
    path(
        'programs/registration/<uuid:registration_id>/verify_profile/<uuid:step_id>/',
        VerifyStudentProfileView.as_view(), name=StudentRegistrationStepType.verify_profile
    ),
    path(
        'programs/registration/<uuid:registration_id>/waivers/<uuid:step_id>/',
        SubmitWaiversView.as_view(), name=StudentRegistrationStepType.submit_waivers
    ),
    path(
        'programs/registration/<uuid:registration_id>/availability/<uuid:step_id>/',
        StudentAvailabilityView.as_view(), name=StudentRegistrationStepType.time_availability
    ),
    path(
        'programs/registration/<uuid:registration_id>/preferences/<uuid:step_id>/',
        InitiatePreferenceEntryView.as_view(), name=StudentRegistrationStepType.lottery_preferences
    ),
    path(
        'programs/registration/<uuid:registration_id>/submit/<uuid:step_id>/',
        ConfirmRegistrationSubmissionView.as_view(), name=StudentRegistrationStepType.submit_registration
    ),
    path(
        'programs/registration/<uuid:registration_id>/lottery_results/<uuid:step_id>/',
        ConfirmAssignedCoursesView.as_view(), name=StudentRegistrationStepType.confirm_assigned_courses
    ),
    path(
        'programs/registration/<uuid:registration_id>/fees/<uuid:step_id>/',
        PayProgramFeesView.as_view(), name=StudentRegistrationStepType.pay_program_fees
    ),
    path(
        'programs/registration/<uuid:registration_id>/surveys/<uuid:step_id>/',
        CompleteSurveysView.as_view(), name=StudentRegistrationStepType.complete_surveys
    ),

    # Registration step additional views
    path(
        'programs/registration/<uuid:registration_id>/preferences/<uuid:step_id>/round_<int:index>/',
        PreferenceEntryRoundView.as_view(), name="preference_entry_round"),
    path(
        'programs/registration/<uuid:registration_id>/step/<uuid:step_id>/complete/',
        RegistrationStepCompleteView.as_view(), name="complete_registration_step",
    ),

    # Scheduler
    path("scheduler/", SchedulerView.as_view(), name="scheduler"),  # TODO: make program specific url
    path("api/v0/classrooms/", ClassroomApiView.as_view(), name="classroom_api"),
    path("api/v0/courses/", CourseApiView.as_view(), name="course_api"),
    path("api/v0/course-sections/", CourseSectionApiView.as_view(), name="course_section_api"),
    path("api/v0/time-slots/", TimeSlotApiView.as_view(), name="time_slot_api"),
    path("api/v0/classroom-time-slots/", ClassroomTimeSlotApiView.as_view(), name="classroom_time_slot_api"),
]
