from django.contrib import admin

from common.forms import SiteRedirectPathForm
from common.models import SiteRedirectPath, User

admin.site.register(User)


@admin.register(SiteRedirectPath)
class SiteRedirectPathAdmin(admin.ModelAdmin):
    form = SiteRedirectPathForm
