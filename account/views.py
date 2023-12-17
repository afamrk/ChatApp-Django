from django.shortcuts import render, redirect, reverse
from django.http.response import Http404, HttpResponseForbidden
from .forms import AccountRegistrationForm, AccountUpdate
from django.contrib.auth import authenticate, login
from django.conf import settings
from .models import Account
from django.db.models import Q


def user_registration(request):
    if request.user.is_authenticated:
        return redirect(reverse('home'))

    if request.POST:
        form = AccountRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password1')
            user = authenticate(email=email, password=password)
            login(request, user)
            next = request.GET.get('next', reverse('home'))
            return redirect(next)
    else:
        form = AccountRegistrationForm()
    return render(request, 'account/registration.html', context={'form': form})

# Create your views here.


def user_profile(request, user_id):
    current_user = request.user

    try:
        profile_user = Account.objects.get(pk=user_id)
    except Account.DoesNotExist:
        raise Http404

    context = {
        'is_self': current_user == profile_user,
        'is_friend': True,
        'account':  profile_user
    }
    return render(request, 'account/profile.html', context)


def search_user(request):

    context = {'accounts': []}

    if request.method == 'GET':
        search_string = request.GET.get('q')
        if search_string:
            query = Q(username__icontains=search_string) | Q(email__icontains=search_string)
            accounts = Account.objects.filter(query)
            for account in accounts:
                context['accounts'].append((account, False))

    return render(request, 'account/search_user.html', context)


def update_user(request, user_id: int):
    if request.user.id != user_id:
        return HttpResponseForbidden()
    if request.method == 'POST':
        form = AccountUpdate(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect("account:profile", user_id=request.user.id)
    form = AccountUpdate(instance=request.user)
    context= {'form': form, 'DATA_UPLOAD_MAX_MEMORY_SIZE': settings.DATA_UPLOAD_MAX_MEMORY_SIZE}
    return render(request, 'account/edit_account.html', context)
