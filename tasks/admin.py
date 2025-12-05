from django.contrib import admin
from .models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "owner",
        "priority",
        "status",
        "due_date",
        "created_at",
    )
    list_filter = ("priority", "status", "created_at")
    search_fields = ("title", "description", "owner__username")
    ordering = ("due_date",)


# Register your models here.
