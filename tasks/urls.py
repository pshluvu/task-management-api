from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import TaskViewSet, RegisterView, home

router = DefaultRouter()
router.register(r'tasks', TaskViewSet, basename='task')

urlpatterns = [
    path('', home),
    path('register/', RegisterView.as_view(), name='register'),
    path('', include(router.urls)),
]

