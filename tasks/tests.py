
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from datetime import timedelta, datetime
import pytz

from .models import Task

User = get_user_model()


class TaskAPITest(APITestCase):

    def setUp(self):
        # ✅ Create users
        self.user1 = User.objects.create_user(
            username="user1",
            password="password123"
        )

        self.user2 = User.objects.create_user(
            username="user2",
            password="password123"
        )

        # ✅ FORCE AUTH (BYPASS JWT COMPLETELY)
        self.client.force_authenticate(user=self.user1)

        # ✅ Create tasks
        self.task_user1 = Task.objects.create(
            owner=self.user1,
            title="User1 Task",
            description="Task for user 1",
            priority=Task.PRIORITY_LOW,
            status=Task.STATUS_PENDING,
            due_date=datetime.now(pytz.UTC) + timedelta(days=2),
        )

        self.task_user2 = Task.objects.create(
            owner=self.user2,
            title="User2 Task",
            description="Task for user 2",
            priority=Task.PRIORITY_HIGH,
            status=Task.STATUS_COMPLETED,
            due_date=datetime.now(pytz.UTC) + timedelta(days=3),
        )

        self.list_url = "/api/tasks/"

    # ✅ 1. CREATE TASK
    def test_create_task(self):
        data = {
            "title": "New Task",
            "description": "Created via test",
            "priority": Task.PRIORITY_LOW,
            "status": Task.STATUS_PENDING,
            "due_date": (datetime.now(pytz.UTC) + timedelta(days=4)).isoformat(),
        }

        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    # ✅ 2. USER CANNOT SEE OTHERS' TASKS
    def test_user_cannot_see_others_tasks(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        for task in response.data:
            self.assertEqual(task["owner"], self.user1.username)

    # ✅ 3. MARK COMPLETE BLOCKS EDITING
    def test_mark_complete_blocks_editing(self):
        url = f"/api/tasks/{self.task_user1.id}/mark-complete/"
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        edit_url = f"/api/tasks/{self.task_user1.id}/"
        response = self.client.patch(edit_url, {"title": "Updated"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # ✅ 4. MARK INCOMPLETE ALLOWS EDIT
    def test_mark_incomplete_allows_edit(self):
        self.task_user1.status = Task.STATUS_COMPLETED
        self.task_user1.save()

        url = f"/api/tasks/{self.task_user1.id}/mark-incomplete/"
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        edit_url = f"/api/tasks/{self.task_user1.id}/"
        response = self.client.patch(edit_url, {"title": "Updated"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # ✅ 5. FILTER COMPLETED TASKS
    def test_filter_completed_tasks(self):
        response = self.client.get("/api/tasks/?status=completed")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    # ✅ 6. FILTER PENDING TASKS
    def test_filter_pending_tasks(self):
        response = self.client.get("/api/tasks/?status=pending")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
