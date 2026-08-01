from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User

from .models import Profile


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'


class BluParkUserAdmin(UserAdmin):
    inlines = (ProfileInline,)
    list_display = UserAdmin.list_display + ('get_role',)

    @admin.display(description='Role')
    def get_role(self, obj):
        return obj.profile.get_role_display()


admin.site.unregister(User)
admin.site.register(User, BluParkUserAdmin)
