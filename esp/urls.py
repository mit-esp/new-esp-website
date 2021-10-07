from django.urls import path

from esp.views import (CourseCreateView, CourseListView, CourseUpdateView,
                       ProgramCreateView, ProgramListView,
                       ProgramStageCreateView, ProgramStageUpdateView,
                       ProgramUpdateView, RegisterView)

urlpatterns = [
    path('register', RegisterView.as_view(), name="register"),

    path('programs/create/', ProgramCreateView.as_view(), name='create_program'),
    path('programs/update/<uuid:pk>/', ProgramUpdateView.as_view(), name='update_program'),
    path('programs/<uuid:pk>/stages/create/', ProgramStageCreateView.as_view(), name="create_program_stage"),
    path('programs/stages/update/<uuid:pk>/', ProgramStageUpdateView.as_view(), name="update_program_stage"),
    path('programs/all/', ProgramListView.as_view(), name='programs'),

    path('classes/create/', CourseCreateView.as_view(), name='create_course'),
    path('classes/update/<uuid:pk>/', CourseUpdateView.as_view(), name='update_course'),
    path('classes/all/', CourseListView.as_view(), name='coursees'),
]
