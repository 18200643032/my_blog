from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import Profile


#定义一个行内admin

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = "UserProfile"

#将profle关联到User中
class UserAdmin(BaseUserAdmin):
    inlines = (ProfileInline,)

#重新注册User
admin.site.unregister(User)
admin.site.register(User,UserAdmin)