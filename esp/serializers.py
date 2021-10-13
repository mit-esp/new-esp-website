from rest_framework import serializers

from esp.models import ClassPreference, ClassSection, Course


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

    class Meta:
        model = ClassPreference
        fields = (
            "class_section",
            "category",
        )

    def create(self, validated_data):
        if self.context.get("group_sections_by_course"):
            course = validated_data["class_section"]
            preferences = []
            for section_id in course.sections.values_list("id", flat=True):
                preferences.append(self.create_single_preference(section_id, validated_data["category"]))
            return preferences
        return self.create_single_preference(validated_data["class_section"].id, validated_data["category"])

    def create_single_preference(self, section_id, category):
        return ClassPreference.objects.update_or_create(
            class_section_id=section_id,
            registration=self.context["registration"],
            defaults={
                "category": category,
            },
        )
