from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from notifications.models import Notification
from django.utils import timezone
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver


# Create your models here.


class PrivateChatRoom(models.Model):
    user1 = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user1')
    user2 = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user2')

    connected_users = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='connected_users')

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.user1} - {self.user2}'

    def connect_user(self, user):
        if user not in self.connected_users.all():
            self.connected_users.add(user)

    def disconnect_user(self, user):
        if user in self.connected_users.all():
            self.connected_users.remove(user)

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


class UnreadMessages(models.Model):
    room = models.ForeignKey(PrivateChatRoom, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    timestamp = models.DateTimeField()
    count = models.IntegerField(default=0)
    recent_message = models.CharField(max_length=500, blank=True, null=True)
    notifications = GenericRelation(Notification)

    def __str__(self):
        return f'{self.room.id} - {self.user.username} - {self.recent_message}'

    def save(self, *args, **kwargs):
        if self.id is None:
            self.timestamp = timezone.now()
        super().save(*args, **kwargs)

    def other_user(self):
        if self.user == self.room.user1:
            return self.room.user2
        else:
            return self.room.user1


@receiver(post_save, sender=PrivateChatRoom)
def create_unread_message_obj(sender, instance, created, **kwargs):
    if created:
        UnreadMessages(room=instance, user=instance.user1).save()
        UnreadMessages(room=instance, user=instance.user2).save()


@receiver(pre_save, sender=UnreadMessages)
def update_unread_message(sender, instance, **kwargs):
    if instance.id is None:
        return
    previous = UnreadMessages.objects.get(id=instance.id)
    content_type = ContentType.objects.get_for_model(instance)
    other_user = instance.other_user()
    if previous.count < instance.count:
        try:
            notification = Notification.objects.get(content_type=content_type, object_id=instance.id)
            notification.verb = instance.recent_message
            notification.timestamp = timezone.now()
            notification.save()
        except Notification.DoesNotExist:
            instance.notifications.create(
                from_user=instance.user,
                target=other_user,
                verb=instance.recent_message,
                redirect_url=f"/chat/?room_id={instance.room.id}",  # we want to go to the chatroom
            )
    elif instance.count == 0:
        try:
            notification = Notification.objects.get(content_type=content_type, object_id=instance.id)
            # notification.read = True
            # notification.save()
            notification.delete()
        except Notification.DoesNotExist:
            pass

