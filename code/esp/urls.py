from django.urls import path
from django.views.generic import TemplateView

from esp.constants import StudentRegistrationStepType
from esp.views.admin_views import (AdminCheckinTeachersView, AdminCommentView,
                                   AdminCourseCreateView, AdminCourseListView,
                                   AdminCourseUpdateView,
                                   AdminCreateCourseSectionsView,
                                   AdminDashboardView,
                                   AdminManageClassroomAvailabilityView,
                                   AdminManageStudentsView,
                                   AdminManageTeachersView,
                                   ApproveFinancialAidView, ClassroomListView,
                                   PrintStudentSchedulesView,
                                   ProgramCreateView, ProgramListView,
                                   ProgramLotteryView, ProgramStageCreateView,
                                   ProgramStageUpdateView, ProgramUpdateView,
                                   SendEmailsView, StudentCashPaymentView,
                                   StudentCheckinView, TeacherCheckinView)
from esp.views.scheduler_views import (AssignClassroomTimeSlotsApiView,
                                       ClassroomApiView,
                                       ClassroomTimeSlotApiView, CourseApiView,
                                       SchedulerView,
                                       TeacherAvailabilityApiView,
                                       TimeSlotApiView)
from esp.views.student_registration_views import (
    CompleteSurveysView, ConfirmAssignedCoursesView,
    ConfirmRegistrationSubmissionView, DeleteCourseRegistrationView,
    EditAssignedCoursesView, InitiatePreferenceEntryView, MakePaymentView,
    PayProgramFeesView, PreferenceEntryRoundView,
    ProgramRegistrationCreateView, ProgramRegistrationStageView,
    RegistrationStepCompleteView, RequestFinancialAidView,
    StudentAvailabilityView, SubmitWaiversView, VerifyStudentProfileView)
from esp.views.teacher_registration_views import (
    AddCoTeacherView, TeacherEditCourseView, TeacherProgramDashboardView,
    TeacherProgramRegistrationCreateView, TeacherRegistrationStepRouterView)
from esp.views.user_views import (GuardianDashboardView, RegisterAccountView,
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
    path('admin/email/', SendEmailsView.as_view(), name="send_email"),
    path('admin/programs/create/', ProgramCreateView.as_view(), name='create_program'),
    path('admin/programs/update/<uuid:pk>/', ProgramUpdateView.as_view(), name='update_program'),
    path('admin/programs/<uuid:pk>/stages/create/', ProgramStageCreateView.as_view(), name="create_program_stage"),
    path('admin/programs/<uuid:pk>/stages/update/', ProgramStageUpdateView.as_view(), name="update_program_stage"),
    path('admin/programs/all/', ProgramListView.as_view(), name='programs'),

    path('admin/programs/<uuid:pk>/classes/create/', AdminCourseCreateView.as_view(), name='create_course'),
    path('admin/programs/<uuid:pk>/classes/update/<uuid:class_pk>/', AdminCourseUpdateView.as_view(), name='update_course'),
    path('admin/programs/<uuid:pk>/classes/', AdminCourseListView.as_view(), name='courses'),
    path('admin/programs/<uuid:pk>/lottery/', ProgramLotteryView.as_view(), name="program_lottery"),
    path(
        'admin/programs/<uuid:pk>/approve_financial_aid/',
        ApproveFinancialAidView.as_view(), name="approve_financial_aid"
    ),
    path('admin/classrooms/', ClassroomListView.as_view(), name="classrooms"),
    path(
        'admin/programs/<uuid:pk>/print/schedules/', PrintStudentSchedulesView.as_view(), name="print_student_schedules"
    ),
    path('admin/programs/<uuid:pk>/manage/students/', AdminManageStudentsView.as_view(),
         name="manage_students"),
    path('admin/programs/<uuid:pk>/manage/students/<uuid:student_id>/', AdminManageStudentsView.as_view(),
         name="manage_students_specific"),
    path('admin/programs/<uuid:pk>/manage/students/<uuid:student_id>/checkin/', StudentCheckinView.as_view(),
         name="student_checkin"),
    path('admin/programs/<uuid:program_id>/manage/students/<uuid:student_id>/payment/', StudentCashPaymentView.as_view(),
          name="manage_student_cash_payment"),
    path('admin/programs/<uuid:pk>/manage/students/<uuid:student_id>/comment/', AdminCommentView.as_view(),
         name="add_comment"),

    path('admin/programs/<uuid:pk>/manage/classroom_availability/', AdminManageClassroomAvailabilityView.as_view(),
         name="manage_classroom_availability"),

    path('admin/programs/<uuid:pk>/classes/create_course_sections/', AdminCreateCourseSectionsView.as_view(),
         name="create_course_sections"),

    path('admin/programs/<uuid:pk>/manage/teachers/', AdminManageTeachersView.as_view(),
         name="manage_teachers"),
    path('admin/programs/<uuid:pk>/manage/teachers/<uuid:timeslot_id>/check_in/<str:unit>/',
         AdminCheckinTeachersView.as_view(), name="check_in_teachers"),
    path('admin/programs/<uuid:teacher_id>/check_in/teacher/<uuid:timeslot_id>/<str:unit>/', TeacherCheckinView.as_view(),
         name="teacher_checkin"),

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
        'programs/registration/<uuid:registration_id>/', ProgramRegistrationStageView.as_view(),
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
        PreferenceEntryRoundView.as_view(), name="preference_entry_round"
    ),
    path(
        'programs/registration/<uuid:registration_id>/financial_aid/<uuid:step_id>/',
        RequestFinancialAidView.as_view(), name="request_financial_aid",
    ),
    path('programs/registration/<uuid:registration_id>/pay/<uuid:step_id>/',
         MakePaymentView.as_view(), name="make_payment"),
    path(
        'programs/registration/<uuid:registration_id>/step/<uuid:step_id>/complete/',
        RegistrationStepCompleteView.as_view(), name="complete_registration_step",
    ),

    # Scheduler
    path("scheduler/", SchedulerView.as_view(), name="scheduler"),  # TODO: make program specific url
    path("api/v0/classrooms/", ClassroomApiView.as_view(), name="classroom_api"),
    path("api/v0/programs/<uuid:pk>/courses/", CourseApiView.as_view(), name="course_api"),
    path("api/v0/programs/<uuid:pk>/time-slots/", TimeSlotApiView.as_view(), name="time_slot_api"),
    path(
        "api/v0/programs/<uuid:pk>/teacher-availability/",
        TeacherAvailabilityApiView.as_view(), name="teacher_availability_api"
    ),
    path(
        "api/v0/programs/<uuid:pk>/classroom-time-slots/",
        ClassroomTimeSlotApiView.as_view(), name="classroom_time_slot_api"
    ),
    path(
        "api/v0/programs/<uuid:pk>/assign-classroom-time-slots/",
        AssignClassroomTimeSlotsApiView.as_view(), name="assign_classroom_time_slots_api"
    ),
]

public_pages = [
    # Public pages
    path('', TemplateView.as_view(template_name='public/welcome.html')),
    path('faq/', TemplateView.as_view(template_name='public/faq.html')),
    path('privacy-policy/', TemplateView.as_view(template_name='public/privacy_policy.html'), name="privacy_policy"),
    path('contact-us/', TemplateView.as_view(template_name='public/contact_us.html'), name="contact_us"),
    path('for-parents/', TemplateView.as_view(template_name='public/for_parents.html')),

    path('teach/', TemplateView.as_view(template_name='public/teach.html')),
    path('learn/', TemplateView.as_view(template_name='public/learn.html')),
    path('volunteer/', TemplateView.as_view(template_name='public/volunteer.html')),

    path('splash/', TemplateView.as_view(template_name='public/splash.html')),
    path('hssp/', TemplateView.as_view(template_name='public/hssp.html')),
    path('spark/', TemplateView.as_view(template_name='public/spark.html')),
    path('cascade/', TemplateView.as_view(template_name='public/cascade.html')),
]

urlpatterns += public_pages
