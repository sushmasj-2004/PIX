# faceapp/admin.py

from django.contrib import admin
from .models import User, Attendance, Department

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "department", "is_admin")
    readonly_fields = ("created_at",)
    fields = ("name", "email", "department", "is_admin", "password", "photo", "created_at")
    search_fields = ("name", "email")

    def save_model(self, request, obj, form, change):
        # Get password entered in admin form
        raw_password = form.cleaned_data.get("password")

        # Hash only if:
        # - It is newly entered AND
        # - It is not already hashed
        if raw_password and not raw_password.startswith("pbkdf2_sha256$"):
            obj.set_password(raw_password)

        super().save_model(request, obj, form, change)


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("department_name", "location", "total_employees")


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ("user", "date", "login_time", "logout_time", "working_hours")
    list_filter = ("date",)
