from django.contrib import admin
from django.http import JsonResponse
from django.urls import path, include, re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


def home(request):
    return JsonResponse({
        "message": "Welcome to the Task Management API",
        "docs": {
            "swagger": "/swagger/",
            "redoc": "/redoc/"
        }
    })


schema_view = get_schema_view(
    openapi.Info(
        title="Task Management API",
        default_version="v1",
        description="API documentation for the Task Management System",
        contact=openapi.Contact(email="admin@example.com"),
        license=openapi.License(name="MIT"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path("", home),  # 👈 this fixes your 404
    path("admin/", admin.site.urls),
    path("api/", include("tasks.urls")),

    re_path(r"^swagger/$", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
    re_path(r"^redoc/$", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc-ui"),
]
