import json

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from django.views.generic.list import BaseListView
from rest_framework import status

from common.constants import PermissionType
from common.utils import csrf_exempt_localhost
from common.views import PermissionRequiredMixin
from esp.forms import AssignClassroomTimeSlotsForm
from esp.models.course_scheduling_models import ClassroomTimeSlot
from esp.models.program_models import Classroom, Course, Program, TimeSlot
from esp.models.program_registration_models import TeacherAvailability
from esp.serializers import ClassroomSerializer, CourseSerializer, TeacherAvailabilitySerializer, TimeSlotSerializer, \
    ClassroomTimeSlotSerializer



class SerializerResponseMixin:
    """
    A mixin that can be used to render a JSON response using a DRF serializer
    """
    serializer_class = None

    def render_to_response(self, *_, **__):
        """
        Return a JSON response
        """
        return JsonResponse({"data": self.serializer_class(self.object_list, many=True).data})


# Todo: Remove CSRF exempt?
@method_decorator(csrf_exempt, name="dispatch")
class AssignClassroomTimeSlotsApiView(View):
    # Todo: Protect with auth and admin permissions
    def post(self, *args, **kwargs):
        try:
            data = json.loads(self.request.body)
        except:
            # Todo
            return JsonResponse({}, status=status.HTTP_400_BAD_REQUEST)
        form = AssignClassroomTimeSlotsForm(data)
        if not form.is_valid():
            return JsonResponse({}, status=status.HTTP_400_BAD_REQUEST)
        form.save()
        return JsonResponse({})


class ClassroomApiView(SerializerResponseMixin, BaseListView):
    # Todo: Protect with auth and admin permissions
    model = Classroom
    serializer_class = ClassroomSerializer


class ClassroomTimeSlotApiView(SerializerResponseMixin, BaseListView):
    # Todo: Protect with auth and admin permissions
    serializer_class = ClassroomTimeSlotSerializer

    def get_queryset(self, **kwargs):
        program = get_object_or_404(Program, pk=self.kwargs['pk'])
        return ClassroomTimeSlot.objects.filter(time_slot__program=program).select_related("course_section__course", "time_slot")


class CourseApiView(SerializerResponseMixin, BaseListView):
    # Todo: Protect with auth and admin permissions
    serializer_class = CourseSerializer

    def get_queryset(self, **kwargs):
        program = get_object_or_404(Program, pk=self.kwargs['pk'])
        return Course.objects.filter(program=program)


class SchedulerView(PermissionRequiredMixin, TemplateView):
    permission = PermissionType.use_scheduler
    template_name = "esp/scheduler.html"


class TimeSlotApiView(SerializerResponseMixin, BaseListView):
    # Todo: Protect with auth and admin permissions
    serializer_class = TimeSlotSerializer

    def get_queryset(self, **kwargs):
        program = get_object_or_404(Program, pk=self.kwargs['pk'])
        return (
            TimeSlot
                .objects
                .filter(program=program)
                .prefetch_related(
                    "teacher_availabilities",
                    "teacher_availabilities__registration__course_teachers",
                    "teacher_availabilities__registration__user",
                )
        )


class TeacherAvailabilityApiView(SerializerResponseMixin, BaseListView):
    # Todo: This view is currently unused; delete if not necessary
    # Todo: Protect with auth and admin permissions
    serializer_class = TeacherAvailabilitySerializer

    def get_queryset(self, **kwargs):
        program = get_object_or_404(Program, pk=self.kwargs['pk'])
        return TeacherAvailability.objects.filter(program=program)
