from rest_framework import routers
from django.conf.urls import url
from .views import *

routers = routers.DefaultRouter()
routers.register(r'videos', VideoViewSet)
routers.register(r'comments', CommentViewSet)
urlpatterns = routers.urls
urlpatterns += [
    url(r'^auth/$', auth),
    url(r'^logout/$', logout_view),
    url(r'^register/', register),
    url(r'^me/$',UserViewSet.as_view({'get':'retrieve_user'}),name='user-detail'),
]
