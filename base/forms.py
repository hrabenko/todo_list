from .models import Task, Category
from django import forms

class TaskForm(forms.ModelForm):
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['task_category'].queryset = Category.objects.filter(user=user)

    class Meta:
        model = Task
        fields = ['title', 'description', 'priority', 'task_category', 'complete', 'deadline']

