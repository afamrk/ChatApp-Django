from django.db import models
from django.conf import settings

# Create your models here.


class PrivateChatRoom(models.Model):
    user1 = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user1')
    user2 = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user2')

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.user1} - {self.user2}'

    @property
    def group_name(self):
        return f'PrivateChatRoom-{self.id}'


class PrivateChatMessageManager(models.Manager):
    def by_room(self, room):
        return self.filter(chat_room=room).order_by("-timestamp")


class PrivateChatMessage(models.Model):
    chat_room = models.ForeignKey(PrivateChatRoom, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    content = models.TextField()

    objects = PrivateChatMessageManager()

    def __str__(self):
        return self.content
