from django.urls import path

from esp.views import (ClassCreateView, ClassListView, ClassUpdateView,
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

    path('classes/create/', ClassCreateView.as_view(), name='create_class'),
    path('classes/update/<uuid:pk>/', ClassUpdateView.as_view(), name='update_class'),
    path('classes/all/', ClassListView.as_view(), name='classes'),
]
