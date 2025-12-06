import django_filters
from .models import Task

class TaskFilter(django_filters.FilterSet):
    due_before = django_filters.DateTimeFilter(field_name="due_date", lookup_expr="lte")
    due_after = django_filters.DateTimeFilter(field_name="due_date", lookup_expr="gte")

    class Meta:
        model = Task
        fields = ['status', 'priority', 'due_before', 'due_after']
