from datetime import datetime
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django.db import models
from django.conf import settings
from chat.utils import get_or_create_private_chat
from notifications.models import Notification

# Create your models here.


class FriendList(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='friendlist')
    friends = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='friends')
    notifications = GenericRelation(Notification)

    def __str__(self):
        return self.user.username

    def add_friend(self, account):
        if account not in self.friends.all():
            self.friends.add(account)
            self.save()

            chat = get_or_create_private_chat(self.user, account)
            if not chat.is_active:
                chat.is_active = True
                chat.save()

    def remove_friend(self, account):
        if account in self.friends.all():
            self.friends.remove(account)
            self.save()

            chat = get_or_create_private_chat(self.user, account)
            if chat.is_active:
                chat.is_active = False
                chat.save()

            self.notifications.create(
                target=self.user,
                from_user=account,
                redirect_url=reverse('account:profile', kwargs={'user_id': account.id}),
                verb=f"you are no longer friend with {account.username}"
            )

    def unfriend(self, account):
        self.remove_friend(account)
        account.friendlist.remove_friend(self.user)
        self.save()

    def is_mutual_friends(self, account):
        if account in self.friends.all():
            return True
        return False


class FriedRequest(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sender')
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='receiver')
    is_active = models.BooleanField(default=True, blank=True, null=False)
    notifications = GenericRelation(Notification)

    def __str__(self):
        return self.sender.username

    def accept(self):
        # TODO
        FriendList.objects.get_or_create(user=self.sender)
        FriendList.objects.get_or_create(user=self.receiver)
        self.sender.friendlist.add_friend(self.receiver)
        self.receiver.friendlist.add_friend(self.sender)
        self.is_active = False
        self.save()

        content_type = ContentType.objects.get_for_model(self)
        notification = Notification.objects.get(target=self.receiver, from_user=self.sender,
                                                content_type=content_type, object_id=self.id)
        notification.verb = f"you are now friend with {self.sender.username}"
        notification.read = True
        notification.timestamp = datetime.now()
        notification.save()

        # notification for sender
        self.notifications.create(
            target=self.sender,
            from_user=self.receiver,
            redirect_url=reverse('account:profile', kwargs={'user_id': self.receiver.id}),
            verb=f"you are now friend with {self.receiver.username}"
        )
        return notification

    def decline(self):
        self.is_active = False
        self.save()
        content_type = ContentType.objects.get_for_model(self)
        notification = Notification.objects.get(target=self.receiver, from_user=self.sender,
                                                content_type=content_type, object_id=self.id)
        notification.verb = f"You declined {self.sender.username} friend request"
        notification.read = True
        notification.timestamp = datetime.now()
        notification.save()

        self.notifications.create(
            target=self.sender,
            from_user=self.receiver,
            redirect_url=reverse('account:profile', kwargs={'user_id': self.receiver.id}),
            verb=f"you friend request declined by {self.receiver.username}"
        )

    def cancel(self):
        self.is_active = False
        self.save()


@receiver(post_save, sender=FriedRequest)
def create_notification(sender, instance, created, **kwargs):
    if created:
        instance.notifications.create(
            target=instance.receiver,
            from_user=instance.sender,
            redirect_url=reverse('account:profile', kwargs={'user_id': instance.receiver.id}),
            verb=f"{instance.sender.username} send you a friend reqeust"
        )

