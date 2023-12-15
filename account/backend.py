from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend


class CaseInsensitiveModelBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        username_field = UserModel.USERNAME_FIELD
        if username is None:
            username = kwargs.get(username_field)
        try:
            user = UserModel.objects.get(**{f'{username_field}__iexact': username})
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
        except UserModel.DoesNotExist:
            UserModel().set_password(password)
