from . import views
from django.urls import path, include

app_name = 'account'

urlpatterns = [
   path('register/', views.user_registration, name='register'),
   path('profile/<int:user_id>', views.user_profile, name='profile'),
   path('search/', views.search_user, name='user_search'),
   path('edit/<int:user_id>', views.update_user, name='edit_user'),
]
