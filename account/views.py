from django.shortcuts import render, redirect, reverse
from . import forms
from django.contrib.auth import authenticate, login


def user_registration(request):
    if request.user.is_authenticated:
        return redirect(reverse('home'))

    if request.POST:
        form = forms.AccountRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password1')
            user = authenticate(email=email, password=password)
            login(request, user)
            next = request.GET.get('next', reverse('home'))
            return redirect(next)
    else:
        form = forms.AccountRegistrationForm()
    return render(request, 'account/registration.html', context={'registration_form': form})

# Create your views here.
