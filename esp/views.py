from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, UpdateView

from esp.forms import ClassForm, ProgramForm, RegisterForm
from esp.models import Class, Program


class RegisterView(CreateView):
    template_name = "registration.html"
    form_class = RegisterForm
    success_url = reverse_lazy('index')

###########################################################


class ProgramCreateView(CreateView):
    model = Program
    form_class = ProgramForm
    success_url = reverse_lazy('programs')


class ProgramUpdateView(UpdateView):
    model = Program
    form_class = ProgramForm
    success_url = reverse_lazy('programs')


class ProgramListView(ListView):
    model = Program

###########################################################


class ClassCreateView(CreateView):
    model = Class
    form_class = ClassForm
    success_url = reverse_lazy('programs')


class ClassUpdateView(UpdateView):
    model = Class
    form_class = ClassForm
    success_url = reverse_lazy('programs')


class ClassListView(ListView):
    model = Class


###########################################################
class BaseDashboardView(LoginRequiredMixin, TemplateView):
    login_url = reverse_lazy('index')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class TeacherDashboardView(BaseDashboardView):
    template_name = 'esp/teacher_dashboard.html'


class AdminDashboardView(BaseDashboardView):
    template_name = 'esp/admin_dashboard.html'


class StudentDashboardView(BaseDashboardView):
    template_name = 'esp/student_dashboard.html'


class GuardianDashboardView(BaseDashboardView):
    template_name = 'esp/guardian_dashboard.html'
