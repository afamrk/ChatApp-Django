from django.db import models
from django.conf import settings

# Create your models here.


class FriendList(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    friends = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='friends')

    def __str__(self):
        return self.user.username

    def add_friend(self, account):
        if account not in self.friends.all():
            self.friends.add(account)
            self.save()

    def remove_friend(self, account):
        if account in self.friends.all():
            self.friends.remove(account)
            self.save()

    def unfriend(self, account):
        self.remove_friend(account)
        friends_list = FriendList.objects.get(user=account)
        friends_list.remove_friend(self.user)
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
        self.sender.friends.add(self.receiver)
        self.receiver.friends.add(self.sender)
        self.is_active = True
        self.save()

    def decline(self):
        self.is_active = False
        self.save()

    def cancel(self):
        self.is_active = False
        self.save()