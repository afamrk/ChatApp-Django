from django.db import models
from django.conf import settings
from chat.utils import get_or_create_private_chat

# Create your models here.


class FriendList(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='friendlist')
    friends = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='friends')

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

    def decline(self):
        self.is_active = False
        self.save()

    def cancel(self):
        self.is_active = False
        self.save()