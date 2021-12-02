import json

from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import TemplateView
from django.views.generic.list import BaseListView
from rest_framework import status

from common.constants import PermissionType
from common.utils import csrf_exempt_localhost
from common.views import PermissionRequiredMixin
from esp.forms import AssignClassroomTimeSlotsForm
from esp.models.course_scheduling import ClassroomTimeSlot
from esp.models.program import Classroom, Course, TimeSlot
from esp.serializers import ClassroomSerializer, CourseSerializer, TimeSlotSerializer, \
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
@method_decorator(csrf_exempt_localhost, name="dispatch")
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
    model = ClassroomTimeSlot
    serializer_class = ClassroomTimeSlotSerializer
    queryset = ClassroomTimeSlot.objects.all().select_related("course_section__course", "time_slot")


class CourseApiView(SerializerResponseMixin, BaseListView):
    # Todo: Protect with auth and admin permissions
    model = Course
    serializer_class = CourseSerializer


class SchedulerView(PermissionRequiredMixin, TemplateView):
    permission = PermissionType.use_scheduler
    template_name = "esp/scheduler.html"


class TimeSlotApiView(SerializerResponseMixin, BaseListView):
    # Todo: Protect with auth and admin permissions
    model = TimeSlot
    serializer_class = TimeSlotSerializer
