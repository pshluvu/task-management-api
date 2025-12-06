from rest_framework import viewsets, generics, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.http import HttpResponse
from rest_framework.permissions import IsAuthenticated, AllowAny

from .models import Task
from .serializers import TaskSerializer, UserSerializer
from .permissions import IsOwner
from .filters import TaskFilter   # ✅ advanced filtering

User = get_user_model()


# --------------------------------------------------
# ROOT TEST ENDPOINT
# --------------------------------------------------
def home(request):
    return HttpResponse("✅ Task Management API is running successfully!")


# --------------------------------------------------
# USER REGISTRATION
# --------------------------------------------------
class RegisterView(generics.CreateAPIView):
    """
    Public endpoint to register a new user.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]


# --------------------------------------------------
# TASK VIEWSET
# --------------------------------------------------
class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    queryset = Task.objects.all()  # required for router
    permission_classes = [IsAuthenticated]  # apply globally

    # ✅ Advanced filtering
    filterset_class = TaskFilter

    # ✅ Sorting
    ordering_fields = ["due_date", "priority", "created_at"]

    # ✅ Search
    search_fields = ["title", "description"]

    def get_queryset(self):
        # Users only see their own tasks
        return Task.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_permissions(self):
        """
        Apply IsOwner only for object-level actions (retrieve, update, destroy, mark-complete/incomplete).
        All other actions (list, create) only require authentication.
        """
        if self.action in [
            'retrieve', 'update', 'partial_update', 'destroy',
            'mark-complete', 'mark-incomplete'
        ]:
            return [IsAuthenticated(), IsOwner()]
        return [IsAuthenticated()]

    # --------------------------------------------------
    # ✅ BLOCK EDITING WHEN TASK IS COMPLETED
    # --------------------------------------------------
    def update(self, request, *args, **kwargs):
        task = self.get_object()
        if task.status == Task.STATUS_COMPLETED:
            return Response(
                {"detail": "Completed tasks cannot be edited unless marked incomplete."},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        task = self.get_object()
        if task.status == Task.STATUS_COMPLETED:
            return Response(
                {"detail": "Completed tasks cannot be edited unless marked incomplete."},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().partial_update(request, *args, **kwargs)

    # --------------------------------------------------
    # ✅ MARK COMPLETE
    # --------------------------------------------------
    @action(detail=True, methods=["post"], url_path="mark-complete")
    def mark_complete(self, request, pk=None):
        task = self.get_object()

        if task.status == Task.STATUS_COMPLETED:
            return Response(
                {"detail": "Task is already completed."},
                status=status.HTTP_400_BAD_REQUEST
            )

        task.status = Task.STATUS_COMPLETED
        task.completed_at = timezone.now()
        task.save()

        return Response(self.get_serializer(task).data)

    # --------------------------------------------------
    # ✅ MARK INCOMPLETE
    # --------------------------------------------------
    @action(detail=True, methods=["post"], url_path="mark-incomplete")
    def mark_incomplete(self, request, pk=None):
        task = self.get_object()

        if task.status == Task.STATUS_PENDING:
            return Response(
                {"detail": "Task is already pending."},
                status=status.HTTP_400_BAD_REQUEST
            )

        task.status = Task.STATUS_PENDING
        task.completed_at = None
        task.save()

        return Response(self.get_serializer(task).data)
