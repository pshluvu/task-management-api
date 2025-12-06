from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Task
from django.utils import timezone


# ✅ USER SERIALIZER (REGISTRATION)
class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ["id", "username", "email", "password"]

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


# ✅ TASK SERIALIZER
class TaskSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source="owner.username")

    class Meta:
        model = Task
        fields = "__all__"
        read_only_fields = ["id", "owner", "completed_at", "created_at", "updated_at"]

    # ✅ Prevent editing if completed
    def validate(self, data):
        if self.instance and self.instance.status == "completed":
            raise serializers.ValidationError(
                "Completed tasks cannot be edited unless reverted to pending."
            )
        return data

    # ✅ Validate Future Date
    def validate_due_date(self, value):
        if value <= timezone.now():
            raise serializers.ValidationError("Due date must be in the future.")
        return value
