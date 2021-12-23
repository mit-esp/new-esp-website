from django.core.exceptions import ValidationError
from django.db.models import F, Value, QuerySet
from django.db.models.functions import Concat
from rest_framework import serializers

from common.models import User
from esp.models.course_scheduling_models import CourseSection, ClassroomTimeSlot
from esp.models.program_models import Course, Classroom, TimeSlot
from esp.models.program_registration_models import (ClassPreference,
                                                    PreferenceEntryCategory, TeacherAvailability)


class ClassPreferenceSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.context.get("group_sections_by_course"):
            self.fields["course_section"].queryset = Course.objects.filter(
                program_id=self.context["registration"].program_id
            )
        else:
            self.fields["course_section"].queryset = CourseSection.objects.filter(
                course__program_id=self.context["registration"].program_id
            )
        self.fields["category"].queryset = PreferenceEntryCategory.objects.filter(
            preference_entry_round_id=self.context["preference_entry_round_id"]
        )
        self.fields["category"].allow_null = True
        self.fields["is_deleted"].read_only = False

    class Meta:
        model = ClassPreference
        fields = (
            "course_section",
            "category",
            "is_deleted",
        )

    def is_valid(self, raise_exception=False):
        validated = super().is_valid(raise_exception=raise_exception)
        if not (self.validated_data["category"] or self.validated_data["is_deleted"]):
            if raise_exception:
                raise ValidationError("No category")
            return False
        return validated

    def create(self, validated_data):
        if self.context.get("group_sections_by_course"):
            course = validated_data["course_section"]
            preferences = []
            for section_id in course.sections.values_list("id", flat=True):
                preferences.append(
                    self.create_single_preference(section_id, validated_data["category"], validated_data["is_deleted"])
                )
            return preferences
        return self.create_single_preference(
            validated_data["course_section"].id, validated_data["category"], validated_data["is_deleted"]
        )

    def create_single_preference(self, section_id, category, is_deleted):
        if is_deleted:
            return ClassPreference.objects.filter(
                category__preference_entry_round_id=self.context["preference_entry_round_id"],
                course_section_id=section_id,
                registration=self.context["registration"],
            ).update(is_deleted=True)
        return ClassPreference.objects.filter(
            category__preference_entry_round_id=self.context["preference_entry_round_id"]
        ).update_or_create(
            course_section_id=section_id,
            registration=self.context["registration"],
            is_deleted=False,
            defaults={
                "category": category,
            },
        )


class CourseSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseSection
        fields = (
            "id",
            "course_id",
            "display_id",
        )


class ClassroomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Classroom
        fields = (
            "id",
            "name",
            "description",
            "max_occupants",
        )


class ClassroomTimeSlotSerializer(serializers.ModelSerializer):
    course_id = serializers.CharField(allow_null=True, source="course_section.course_id")
    course_name = serializers.CharField(allow_null=True, source="course_section.course.name")
    course_section = CourseSectionSerializer(read_only=True)
    end_datetime = serializers.DateTimeField(source="time_slot.end_datetime")
    start_datetime = serializers.DateTimeField(source="time_slot.start_datetime")

    class Meta:
        model = ClassroomTimeSlot
        fields = (
            "classroom_id",
            "course_id",
            "course_name",
            "course_section",
            "course_section_id",
            "end_datetime",
            "id",
            "start_datetime",
            "time_slot_id",
        )


class CourseSerializer(serializers.ModelSerializer):
    sections = CourseSectionSerializer(many=True, read_only=True)
    sections_count = serializers.IntegerField(read_only=True, source='sections.count')

    class Meta:
        model = Course
        fields = (
            "admin_notes",
            "description",
            "display_id",
            "end_date",
            "id",
            "name",
            "sections",
            "sections_count",
            "sessions_per_week",
            "start_date",
            "teacher_notes",
            "time_slots_per_session",
        )


class TimeSlotSerializer(serializers.ModelSerializer):
    course_teacher_availabilities = serializers.JSONField("course_teacher_availabilities")

    class Meta:
        model = TimeSlot
        fields = (
            "course_teacher_availabilities",
            "end_datetime",
            "id",
            "start_datetime",
        )


class TeacherAvailabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = TeacherAvailability
        fields = (
            "id",
            "registration",
            "time_slot",
        )


class AssignClassroomTimeSlotSerializer(serializers.Serializer):
    classroom_time_slot_id = serializers.UUIDField(required=True)
    course_section_id = serializers.UUIDField(allow_null=True, required=True)


class UserSerializer(serializers.ModelSerializer):
    search_string = serializers.CharField()

    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "id",
            "username",
            "user_type",
            "verified",
        )

    def __new__(cls, *args, **kwargs):
        if args and isinstance(args[0], QuerySet):
            if hasattr(args[0].first(), "search_string"):
                UserSerializer.Meta.fields += ("search_string",)
        return super().__new__(cls, *args, **kwargs)
