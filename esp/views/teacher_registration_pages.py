from django.shortcuts import redirect
from django.views.generic import TemplateView
from django.views.generic.detail import DetailView, SingleObjectMixin

from common.constants import PermissionType
from common.views import PermissionRequiredMixin
from esp.models.program import Program
from esp.models.program_registration import TeacherRegistration


class TeacherProgramRegistrationCreateView(PermissionRequiredMixin, SingleObjectMixin, TemplateView):
    permission = PermissionType.teacher_register_for_program
    model = Program
    template_name = "teacher/program_registration_create.html"

    def permission_enabled_for_view(self):
        self.object = self.get_object()
        return self.object.show_to_teachers()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["existing_registrations"] = TeacherRegistration.objects.filter(
            program=self.object, user=self.request.user
        )
        return context

    def post(self, request, *args, **kwargs):
        registration, _created = TeacherRegistration.objects.get_or_create(program=self.object, user=self.request.user)
        return redirect("current_registration_stage", pk=registration.id)


class TeacherProgramDashboardView(PermissionRequiredMixin, DetailView):
    permission = PermissionType.teacher_register_for_program
    model = TeacherRegistration
    context_object_name = "registration"
    template_name = "teacher/program_registration_dashboard.html"

    def permission_enabled_for_view(self):
        registration = self.get_object()
        return registration.program.show_to_teachers() or registration.ignore_registration_deadlines()

    def get_queryset(self):
        queryset = super().get_queryset()
        if not self.request.user.has_permission(PermissionType.teacher_registrations_edit_all):
            queryset = queryset.filter(user_id=self.request.user.id)
        return queryset
