from django.contrib import admin

from .models import Employee, Leave, User
from django.contrib.auth.admin import UserAdmin

class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('employee', 'hierarchy', 'leave_count')

class LeaveAdmin(admin.ModelAdmin):
    list_display = ('id', 'employee', 'start', 'end', 'status')

# Register your models here.
admin.site.register(User, UserAdmin)
admin.site.register(Employee, EmployeeAdmin)
admin.site.register(Leave, LeaveAdmin)