from django.db import models
from django.conf import settings

# Create your models here.


class PublicChatRoom(models.Model):
    title = models.CharField(max_length=255, unique=True)
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True)

    def __str__(self):
        return self.title

    def connect_user(self, user):
        if user not in self.users.all():
            self.users.add(user)

    def disconnect_user(self, user):
        if user in self.users.all():
            self.users.remove(user)

    @property
    def group_name(self):
        return f'PublicChatRoom-{self.id}'


class PublicChatMessageManager(models.Manager):
    def by_room(self, room):
        return self.filter(chat_room=room).order_by("-timestamp")


class PublicChatMessages(models.Model):
    chat_room = models.ForeignKey(PublicChatRoom, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    content = models.TextField()

    objects = PublicChatMessageManager()

    def __str__(self):
        return self.content
