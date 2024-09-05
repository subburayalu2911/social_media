from rest_framework import routers
from django.urls import path, include, re_path

from .views import *

router = routers.DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),
    path('login', login),
    path('register', register_user),
    path('user/list/', UserManagement.as_view()),
    path('user/<uuid:user_id>/', UserManagement.as_view()),
    path('send/request/', user_friend_request),
    path('request/friend/list/', friends_list_screen_based),
    path('requested/user/manage/', requested_friends_management.as_view()),
]
