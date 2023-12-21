from django.urls import path
from . import views


app_name = 'friends'
urlpatterns = [
    path('accept_friend_request/', views.accept_friend_request, name='accept_friend_request'),
    path('cancel_friend_request/', views.cancel_friend_request, name='cancel_friend_request'),
    path('decline_friend_request/', views.decline_friend_request, name='decline_friend_request'),
    path('remove_friend/', views.remove_friend, name='remove_friend'),
    path('send_friend_request/', views.send_friend_request, name='send_friend_request'),
    path('show_friend_requests/', views.show_friend_requests, name='show_friend_requests'),
    path('show_friends/<int:user_id>', views.show_friends, name='show_friends'),
]
