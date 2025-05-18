from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    followers = models.ManyToManyField('User', related_name='user_follow', symmetrical=False, blank=True)
    followed = models.ManyToManyField('User', related_name='user_followed', symmetrical=False, blank=True)

    def serialize(self):
        return {
            "id": self.id,
            "username": self.username,
        }

class Post(models.Model):
    user = models.ForeignKey('User', on_delete=models.DO_NOTHING, related_name='post')
    content = models.TextField()
    date = models.DateTimeField()
    like_count = models.ManyToManyField('User', related_name='user_liked', blank=True)

    def serialize(self):
        return {
            "id": self.id,
            "user": self.user.username,
            "content": self.content,
            "date": self.date.strftime("%b %d %Y, %I:%M %p"),
            "likes": self.like_count.count(),
        }

