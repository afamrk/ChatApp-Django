from django.shortcuts import render
from django.http import HttpResponseForbidden, JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from account.models import Account
from .utils import is_request_send
from .models import FriedRequest

# Create your views here.


@login_required
@require_http_methods(["POST"])
def send_friend_request(request):

    user = request.user
    account_id = request.POST.get('user_id')
    try:
        account = Account.objects.get(id=account_id)
        if account == user or account in user.friends.all() or is_request_send(user, account):
            response = {'error': 'Error'}
        else:
            friend_request = FriedRequest(sender=user, receiver=account)
            friend_request.save()
            response = {'success': 'friend request sent'}
    except Account.DoesNotExist:
        response = {'error': 'Error'}
    return JsonResponse(response)


@login_required
def show_friend_requests(request):
    user = request.user
    friend_requests = user.receiver.filter(is_active=True)
    return render(request, 'friends/friend_requests.html',
                  context={'friend_requests': friend_requests})


@login_required
@require_http_methods(['POST'])
def accept_friend_request(request):
    user = request.user
    request_id = request.POST.get('request_id')
    try:
        friend_request = FriedRequest.objects.get(id=request_id)
        if friend_request.receiver == user:
            friend_request.accept()
            response = {'Success': 'accepted'}
        else:
            response = {'Error': ''}
    except FriedRequest.DoesNotExist:
        response = {'Error': ''}
    return JsonResponse(response)


@login_required
@require_http_methods(['POST'])
def decline_friend_request(request):
    user = request.user
    request_id = request.POST.get('request_id')
    try:
        friend_request = FriedRequest.objects.get(id=request_id)
        if friend_request.receiver == user:
            friend_request.decline()
            response = {'Success': 'declined'}
        else:
            response = {'Error': ''}
    except FriedRequest.DoesNotExist:
        response = {'Error': ''}
    return JsonResponse(response)


@login_required
@require_http_methods(['POST'])
def cancel_friend_request(request):
    user = request.user
    request_id = request.POST.get('request_id')
    try:
        friend_request = FriedRequest.objects.get(id=request_id)
        if friend_request.sender == user:
            friend_request.cancel()
            response = {'Success': 'declined'}
        else:
            response = {'Error': ''}
    except FriedRequest.DoesNotExist:
        response = {'Error': ''}
    return JsonResponse(response)

@login_required
@require_http_methods(['POST'])
def remove_friend(request):
    user = request.user
    user_id = request.POST.get('user_id')
    try:
        removee = Account.objects.get(id=user_id)
        user.friendlist.unfriend(removee)
        response = {'Success': 'accepted'}
    except Account.DoesNotExist:
        response = {'Error': ''}
    return JsonResponse(response)


@login_required
def show_friends(request, user_id):
    user = request.user
    try:
        account = Account.objects.get(id=user_id)
    except Account.DoesNotExist:
        return HttpResponseForbidden()
    if not (user == account or user.friendlist.is_mutual_friends(account)):
        return HttpResponseForbidden()
    all_friends = []
    for friend in account.friendlist.friends.all():
        all_friends.append((friend, user.friendlist.is_mutual_friends(friend)))
    return render(request, 'friends/friend_list.html', context={'friends': all_friends})
