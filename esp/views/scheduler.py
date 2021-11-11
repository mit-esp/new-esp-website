from django.http import JsonResponse
from django.views.generic import TemplateView
from django.views.generic.list import BaseListView

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
    model = Classroom
    serializer_class = ClassroomSerializer


class ClassroomTimeSlotApiView(SerializerResponseMixin, BaseListView):
    model = ClassroomTimeSlot
    serializer_class = ClassroomTimeSlotSerializer


class CourseApiView(SerializerResponseMixin, BaseListView):
    model = Course
    serializer_class = CourseSerializer


class CourseSectionApiView(SerializerResponseMixin, BaseListView):
    model = CourseSection
    serializer_class = CourseSectionSerializer


class SchedulerView(TemplateView):
    # TODO: Permissions
    template_name = "esp/scheduler.html"


class TimeSlotApiView(SerializerResponseMixin, BaseListView):
    model = TimeSlot
    serializer_class = TimeSlotSerializer
