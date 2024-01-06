from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.base_user import BaseUserManager
from friends.models import FriendList


class AccountManager(BaseUserManager):
    def create_user(self, email, username, password):
        if not (email and username):
            raise ValueError('username or email not provided')

        user = self.model(
            email=self.normalize_email(email),
            username=username,
        )
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, username, password):
        user = self.create_user(email, username, password)
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save()
        return user

def get_profile_image_path(self, filename):
    return f'/images/{self.pk}/{filename}'


class Account(AbstractBaseUser):
    email = models.EmailField(unique=True, max_length=100)
    username = models.CharField(max_length=100, unique=True)
    join_date = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    profile_image = models.ImageField(max_length=255, upload_to=get_profile_image_path, null=True,
                                      blank=True, default='images/default_profile.png')
    hide_email = models.BooleanField(default=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = AccountManager()

    def __str__(self):
        return self.username

    def has_module_perms(self, app_label):
        return self.is_admin

    def has_perm(self, perm, obj=None):
        return self.is_admin


@receiver(post_save, sender=Account)
def user_save(sender, instance, created, **kwargs):
    if created:
        FriendList.objects.get_or_create(user=instance)