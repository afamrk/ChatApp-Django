from django import forms
from django.contrib.auth.forms import UserCreationForm
from . import models


class AccountRegistrationForm(UserCreationForm):

    class Meta:
        model = models.Account
        fields = ['email', 'username', 'password1', 'password2']

    # def clean_email(self):
    #     email = self.cleaned_data['email'].lower()
    #     try:
    #         models.Account.objects.get(email=email)
    #     except Exception:
    #         return email
    #     raise forms.ValidationError(f'{email} already in user')
    #
    # def clean_username(self):
    #     username = self.cleaned_data['username']
    #     try:
    #         models.Account.objects.get(username=username)
    #     except Exception:
    #         return username
    #     raise forms.ValidationError(f'{username} already in user')


class AccountUpdate(forms.ModelForm):

    class Meta:
        model = models.Account
        fields = ['email', 'username', 'hide_email', 'profile_image']
        widgets = {'profile_image': forms.widgets.FileInput}
