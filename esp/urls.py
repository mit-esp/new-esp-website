from django.urls import path

from esp.views import (RegisterView, ProgramCreateView, ProgramListView, ProgramUpdateView, ClassCreateView, ClassListView, ClassUpdateView, )

urlpatterns = [
    path('register', RegisterView.as_view(), name="register"),

    path(r'program/create/', ProgramCreateView.as_view(), name='create_program'),
    path(r'program/update/(?P<pk>\d+)/', ProgramUpdateView.as_view(), name='update_program'),
    path(r'program/all/', ProgramListView.as_view(), name='programs'),

    path(r'class/create/', ClassCreateView.as_view(), name='create_class'),
    path(r'class/update/(?P<pk>\d+)/', ClassUpdateView.as_view(), name='update_class'),
    path(r'class/all/', ClassListView.as_view(), name='classes'),
]
