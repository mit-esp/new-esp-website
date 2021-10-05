from django.urls import path

from esp.views import (RegisterView, ProgramCreateView, ProgramListView, ProgramUpdateView, ClassCreateView, ClassListView, ClassUpdateView, )

urlpatterns = [
    path('register', RegisterView.as_view(), name="register"),

    path('programs/create/', ProgramCreateView.as_view(), name='create_program'),
    path('programs/update/<uuid:pk>/', ProgramUpdateView.as_view(), name='update_program'),
    path('programs/all/', ProgramListView.as_view(), name='programs'),

    path('classes/create/', ClassCreateView.as_view(), name='create_class'),
    path('classes/update/<uuid:pk>/', ClassUpdateView.as_view(), name='update_class'),
    path('classes/all/', ClassListView.as_view(), name='classes'),
]
