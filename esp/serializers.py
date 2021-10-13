from esp.models import ClassPreference, ClassSection, Course
from rest_framework import serializers


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
            for section_id in course.sections.values_list("id", flat=True):
                ClassPreference.objects.update_or_create(
                    class_section_id=section_id,
                    registration=self.context["registration"],
                    category=validated_data["category"],
                )
            return
        return ClassPreference.objects.update_or_create(
            class_section=validated_data["class_section"],
            registration=self.context["registration"],
            category=validated_data["category"],
        )
