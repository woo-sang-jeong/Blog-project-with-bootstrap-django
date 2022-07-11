from django.db import models

# Create your models here.

from django.db import models

class Post(models.Model):
    title = models.CharField(max_length=30)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    #author: 나중에 추가

    def __str__(self):
        return f'[{self.pk}][{self.title}]'