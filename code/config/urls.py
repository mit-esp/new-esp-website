"""config URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import include
from django.contrib import admin
from django.http import HttpResponse
from django.urls import path
from django_ses.views import SESEventWebhookView

from common.views import SiteRedirectView

urlpatterns = [
    path('', include("common.urls")),
    path('', include("esp.urls")),
    path('django_admin/', admin.site.urls, name="django_admin"),
    path("health_check/", lambda request: HttpResponse("ok")),
    path("ses/event-webhook/", SESEventWebhookView.as_view(), name="handle-event-webhook"),
    # Warning: must come last!
    path('<path:path>/', SiteRedirectView.as_view(), name="site_redirect"),
]
