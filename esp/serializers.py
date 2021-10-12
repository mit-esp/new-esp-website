from django.core.exceptions import ValidationError
from rest_framework import serializers

from esp.models import (ClassPreference, ClassSection, Course,
                        PreferenceEntryCategory)


class ClassPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassPreference
        fields = (
            "class_section_id",
            "category_id",
        )

    def validate_class_section_id(self, value):
        if self.context.get("group_sections_by_course"):
            if not Course.objects.filter(id=value, program_id=self.context["registration"].program_id).exists():
                raise ValidationError("Nonexistent class")
        else:
            if not (
                ClassSection.objects
                    .filter(id=value, course__program_id=self.context["registration"].program_id).exists()
            ):
                raise ValidationError("Nonexistent class")
        return value

    def validate_category_id(self, value):
        if not PreferenceEntryCategory.objects.filter(
            id=value, preference_entry_round_id=self.context["preference_entry_round_id"]
        ).exists:
            raise ValidationError("Nonexistent category")
        return value

    def create(self, validated_data):
        print("hi")
        self.is_valid()
        print(self.validated_data)
        if self.context.get("group_sections_by_course"):
            course = Course.objects.get(id=validated_data["class_section_id"])
            for section_id in course.sections.values_list("id", flat=True):
                ClassPreference.objects.update_or_create(
                    class_section_id=section_id,
                    registration_id=self.context["registration"].id,
                    category_id=validated_data["category_id"],
                )
            return
        return ClassPreference.objects.update_or_create(
            class_section_id=validated_data["class_section_id"],
            registration_id=self.context["registration_id"],
            category_id=validated_data["category_id"],
        )
