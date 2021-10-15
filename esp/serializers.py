from django.core.exceptions import ValidationError
from rest_framework import serializers

from esp.models import (ClassPreference, ClassSection, Course,
                        PreferenceEntryCategory)


class ClassPreferenceSerializer(serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.context.get("group_sections_by_course"):
            self.fields["class_section"].queryset = Course.objects.filter(
                program_id=self.context["registration"].program_id
            )
        else:
            self.fields["class_section"].queryset = ClassSection.objects.filter(
                course__program_id=self.context["registration"].program_id
            )
        self.fields["category"].queryset = PreferenceEntryCategory.objects.filter(
            preference_entry_round_id=self.context["preference_entry_round_id"]
        )
        self.fields["category"].allow_null = True

    class Meta:
        model = ClassPreference
        fields = (
            "class_section",
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
            course = validated_data["class_section"]
            preferences = []
            for section_id in course.sections.values_list("id", flat=True):
                preferences.append(
                    self.create_single_preference(section_id, validated_data["category"], validated_data["is_deleted"])
                )
            return preferences
        return self.create_single_preference(
            validated_data["class_section"].id, validated_data["category"], validated_data["is_deleted"]
        )

    def create_single_preference(self, section_id, category, is_deleted):
        if is_deleted:
            return ClassPreference.objects.filter(
                category__preference_entry_round_id=self.context["preference_entry_round_id"],
                class_section_id=section_id,
                registration=self.context["registration"],
            ).update(is_deleted=True)
        return ClassPreference.objects.filter(
            category__preference_entry_round_id=self.context["preference_entry_round_id"]
        ).update_or_create(
            class_section_id=section_id,
            registration=self.context["registration"],
            is_deleted=False,
            defaults={
                "category": category,
            },
        )
