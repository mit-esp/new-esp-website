from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from django.views.generic.list import BaseListView

from common.constants import PermissionType
from common.utils import csrf_exempt_localhost
from common.views import PermissionRequiredMixin
from esp.models.course_scheduling import CourseSection, ClassroomTimeSlot
from esp.models.program import Classroom, Course, TimeSlot
from esp.serializers import ClassroomSerializer, CourseSerializer, CourseSectionSerializer, TimeSlotSerializer, \
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


class ClassroomApiView(SerializerResponseMixin, BaseListView):
    #todo: protect with auth and admin permissions
    model = Classroom
    serializer_class = ClassroomSerializer


@method_decorator(csrf_exempt_localhost, name="dispatch")
class ClassroomTimeSlotApiView(SerializerResponseMixin, BaseListView):
    #todo: protect with auth and admin permissions
    model = ClassroomTimeSlot
    serializer_class = ClassroomTimeSlotSerializer
    queryset = ClassroomTimeSlot.objects.all().select_related("course_section__course")

    def post(self, *args, **kwargs):

        return JsonResponse({})


class CourseApiView(SerializerResponseMixin, BaseListView):
    #todo: protect with auth and admin permissions
    model = Course
    serializer_class = CourseSerializer


class SchedulerView(PermissionRequiredMixin, TemplateView):
    permission = PermissionType.use_scheduler
    template_name = "esp/scheduler.html"


class TimeSlotApiView(SerializerResponseMixin, BaseListView):
    #todo: protect with auth and admin permissions
    model = TimeSlot
    serializer_class = TimeSlotSerializer
