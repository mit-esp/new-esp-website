from django.conf import settings
from django.conf.urls import url
from django.contrib.auth import views as auth_views
from django.urls import include, path

from common import views

urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path('login/', auth_views.LoginView.as_view(template_name='common/login.html'), name='login'),
    path("logout", views.LogoutView.as_view(), name="logout"),
]

if settings.DEBUG_TOOLBAR:
    import debug_toolbar

    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]
