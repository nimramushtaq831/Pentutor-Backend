from django.db import models
from django.contrib.auth.models import User

class Chat(models.Model):
    room_name = models.CharField(max_length=250)
    allowed_user = models.CharField(max_length=250)

# Create your models here.
