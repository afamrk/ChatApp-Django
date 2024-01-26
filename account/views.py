from django.shortcuts import render, redirect, reverse
from django.http.response import Http404, HttpResponseForbidden
from .forms import AccountRegistrationForm, AccountUpdate
from django.contrib.auth import authenticate, login
from django.conf import settings
from .models import Account
from django.db.models import Q
from friends.utils import is_request_send, FriendRequestStatus


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
    user = request.user
    try:
        account = Account.objects.get(pk=user_id)
    except Account.DoesNotExist:
        raise Http404

    all_friends = account.friendlist.friends.all()
    is_self = user == account
    is_friend = user in all_friends
    request_sent = FriendRequestStatus.NO_REQUEST_SENT.value
    friend_requests = None
    pending_friend_request = FriendRequestStatus.NO_REQUEST_SENT.value

    if not is_self and user.is_authenticated:
        pending_friend_request = is_request_send(user, account)
        if pending_friend_request:
            request_sent = FriendRequestStatus.YOU_SENT_TO_THEM.value
        else:
            pending_friend_request = is_request_send(account, user)
            if pending_friend_request:
                request_sent = FriendRequestStatus.THEM_SENT_TO_YOU.value
    elif user.is_authenticated:
        friend_requests = user.receiver.filter(is_active=True)
    else:
        pass

    context = {
        'is_self': is_self,
        'is_friend': is_friend,
        'account':  account,
        'friends': all_friends,
        'request_sent': request_sent,
        'friend_requests': friend_requests,
        'pending_friend_request': pending_friend_request
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
                is_friend = account.friendlist.is_mutual_friends(request.user)
                context['accounts'].append((account, is_friend))

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

[403, 339, 221, 286, 179, 252, 175, 486, 259, 93, 118, 419, 298, 312, 306, 319, 344, 172, 149, 339, 329]