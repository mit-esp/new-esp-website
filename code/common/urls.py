from django.conf import settings
from django.urls import re_path
from django.contrib.auth import views as auth_views
from django.urls import include, path

from common import views

urlpatterns = [
    path("dashboard/", views.IndexView.as_view(), name="index"),  #todo: rename index to dashboard
    path('login/', auth_views.LoginView.as_view(template_name='common/login.html'), name='login'),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("accounts/password_change/", auth_views.PasswordChangeView.as_view(), name='password_change'),
    path("accounts/password_change/done/", auth_views.PasswordChangeDoneView.as_view(), name='password_change_done'),
    path('accounts/password_reset/', auth_views.PasswordResetView.as_view(), name="password_reset"),
    path('accounts/password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path(
        'accounts/reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'
    ),
    path('accounts/reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]

if settings.DEBUG_TOOLBAR:
    import debug_toolbar

    urlpatterns += [
        re_path(r'^__debug__/', include(debug_toolbar.urls)),
    ]
