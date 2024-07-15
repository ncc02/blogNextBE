from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model

class Blog(models.Model):
    created = models.DateTimeField(auto_now_add=True) 
    image = models.ImageField(upload_to='blog_images/', blank=True, null=True, default='')
    title = models.CharField(max_length=255, blank=True, default='')
    content = models.TextField(blank=True, null=True)
    author = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='blogs', null=True, blank=True)
    class Meta:
        ordering = ['-created']
# Create your models here.

