from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission


class User(AbstractUser):
    groups = models.ManyToManyField(Group, related_name='group_users')
    user_permissions = models.ManyToManyField(Permission, related_name='user_permissions_users')
    # ...
# Create your models here.
