from django.contrib.auth import login
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, TemplateView, UpdateView

from common.constants import PermissionType, UserType
from common.views import PermissionRequiredMixin
from esp.forms import (RegisterUserForm, StudentProfileForm,
                       TeacherProfileForm, UpdateStudentProfileForm)
from esp.models.program import Program
from esp.models.program_registration import StudentProfile

######################################
# SHARED PAGES
######################################


class RegisterAccountView(CreateView):
    template_name = "esp/registration.html"
    form_class = RegisterUserForm

    def get_success_url(self):
        profile_form_url_mapping = {
            UserType.student: "create_student_profile",
            UserType.teacher: "create_teacher_profile",
        }
        # If profile info required, redirect to profile form; otherwise redirect to dashboard
        return reverse(profile_form_url_mapping.get(self.object.user_type, self.object.get_dashboard_url()))

    def form_valid(self, form):
        login(self.request, form.user)
        return super().form_valid(form)


class BaseDashboardView(PermissionRequiredMixin, TemplateView):
    login_url = reverse_lazy('index')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


###################################################################
# STUDENT PAGES
###################################################################

class StudentProfileCreateView(PermissionRequiredMixin, CreateView):
    permission = PermissionType.student_create_profile
    model = StudentProfile
    form_class = StudentProfileForm
    template_name = "student/student_profile_create_form.html"
    success_url = reverse_lazy("student_dashboard")

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class StudentProfileUpdateView(PermissionRequiredMixin, UpdateView):
    permission = PermissionType.student_update_profile
    model = StudentProfile
    form_class = UpdateStudentProfileForm
    template_name = "student/student_profile_update_form.html"
    success_url = reverse_lazy("student_dashboard")

    def get_initial(self):
        return {
            "first_name": self.object.user.first_name,
            "last_name": self.object.user.last_name,
            "email": self.object.user.email,
        }

    def form_valid(self, form):
        self.object.user.update(
            first_name=form.cleaned_data["first_name"], last_name=form.cleaned_data["last_name"],
            email=form.cleaned_data["email"]
        )
        return super().form_valid(form)


class StudentDashboardView(BaseDashboardView):
    permission = PermissionType.student_dashboard_view
    template_name = 'student/student_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_registrations = self.request.user.registrations.filter(
            program__show_to_students_on__lte=timezone.now(),
            program__hide_from_students_on__gt=timezone.now()
        )
        context["registrations"] = user_registrations
        print(user_registrations.values("program_id"))
        eligible_programs = Program.objects.exclude(
            id__in=user_registrations.values("program_id")
        ).filter(
            show_to_students_on__lte=timezone.now(),
            hide_from_students_on__gte=timezone.now(),
        )
        try:
            grade_level = self.request.user.student_profile.grade_level()
            eligible_programs = eligible_programs.exclude(
                max_grade_level__lt=grade_level,
                min_grade_level__gt=grade_level,
            )
        except StudentProfile.DoesNotExist:
            eligible_programs = None
        context["eligible_programs"] = eligible_programs
        return context


##########################################################
# TEACHER PAGES
##########################################################

class TeacherProfileCreateView(PermissionRequiredMixin, CreateView):
    permission = PermissionType.teacher_create_profile
    form_class = TeacherProfileForm
    template_name = "teacher/teacher_profile_create_form.html"


class TeacherProfileUpdateView(PermissionRequiredMixin, UpdateView):
    permission = PermissionType.teacher_update_profile
    form_class = TeacherProfileForm
    template_name = "teacher/teacher_profile_update_form.html"


class TeacherDashboardView(BaseDashboardView):
    permission = PermissionType.teacher_dashboard_view
    template_name = "teacher/teacher_dashboard.html"


#######################################################


class AdminDashboardView(BaseDashboardView):
    permission = PermissionType.admin_dashboard_view
    template_name = 'dashboards/admin_dashboard.html'


class GuardianDashboardView(BaseDashboardView):
    template_name = 'dashboards/guardian_dashboard.html'


class VolunteerDashboardView(BaseDashboardView):
    permission = PermissionType.volunteer_program_dashboard_view
    template_name = 'dashboards/volunteer_dashboard.html'
