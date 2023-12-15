from . import views
from django.urls import path


urlpatterns = [
   path('register/', views.user_registration, name='register')
]