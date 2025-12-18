from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import Task

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ("id", "username", "email", "password")

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data.get("email"),
            password=validated_data["password"],
        )
        return user


class TaskSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source="owner.username")

    class Meta:
        model = Task
        fields = (
            "id",
            "owner",
            "title",
            "description",
            "due_date",
            "priority",
            "status",
            "completed_at",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "owner", "completed_at", "created_at", "updated_at")

    def validate_due_date(self, value):
        if value <= timezone.now():
            raise serializers.ValidationError("Due date must be in the future.")
        return value

    def validate(self, data):
        # Prevent editing completed tasks unless status is being set back to pending
        instance = getattr(self, "instance", None)
        if instance and instance.status == Task.STATUS_COMPLETED:
            # if status field not provided or is still completed, block modifications
            new_status = data.get("status", instance.status)
            if new_status == Task.STATUS_COMPLETED:
                # allow no other changes (must revert to pending to edit)
                # check whether any non-status fields would change
                immutable_fields = ("title", "description", "due_date", "priority")
                for f in immutable_fields:
                    if f in data and getattr(instance, f) != data[f]:
                        raise serializers.ValidationError(
                            "Completed tasks cannot be edited. Revert to pending to edit."
                        )
        return data
