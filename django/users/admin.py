from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User


from .forms import CustomUserForm

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserForm
    form = CustomUserForm
    model = User
    list_display = ['email', 'username', 'is_staff']


# admin.site.register(CustomUserAdmin)
