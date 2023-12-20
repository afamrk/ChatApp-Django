from django.shortcuts import render
from django.http import HttpResponseForbidden, JsonResponse
from django.views.decorators.http import require_http_methods
from account.models import Account
from .utils import is_request_send
from .models import FriedRequest

# Create your views here.


@require_http_methods(["POST"])
def send_friend_request(request):
    user = request.user
    if not user.is_authenticated:
        return HttpResponseForbidden('not allowed')

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


