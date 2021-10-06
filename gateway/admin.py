from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import SiteOwner, Gateway


@admin.register(SiteOwner)
class UserAdmin(admin.ModelAdmin):
    pass


admin.site.register(Gateway)
