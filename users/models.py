from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.CharField(max_length=255, blank=True)
    # другие поля профиля


class Friend(models.Model):
    from_user = models.ForeignKey(User, related_name='friends', on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name='friend_requests', on_delete=models.CASCADE)
    accepted = models.BooleanField(default=False)
# Create your models here.
