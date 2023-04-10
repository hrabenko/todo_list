from django.db import models
from django.contrib.auth.models import User

class Task(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    complete = models.BooleanField(default=False)
    create = models.DateTimeField(auto_now_add=True)

    PRIORITY_LIST = [("H", "High"), ("M", "Medium"), ("L", "Low")]

    priority = models.CharField(max_length=1, choices=PRIORITY_LIST, default='H')
    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['complete']
