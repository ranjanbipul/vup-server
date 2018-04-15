# Python imports
import urllib
import json

# Django imports
from django.conf import settings
from django.http.response import JsonResponse
from django.db import transaction
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response
from rest_framework import viewsets, permissions, mixins, status
from rest_framework.decorators import api_view, detail_route
# Application imports
from .serializers import *

@require_http_methods(['POST'])
@csrf_exempt
def auth(request):
    data = json.loads(request.body.decode("utf-8"))
    user = authenticate(request, username=data["username"], password=data["password"])
    if user is not None:
        login(request, user)
        return JsonResponse({"status": "OK", "message": "You have successfully logged in."})
    else:
        return JsonResponse({"non_field_errors": ["Authentication failed! Check your username and password."]}, status=400)

@require_http_methods(['POST'])
@csrf_exempt
def logout_view(request):
    logout(request)
    return JsonResponse({"status":"OK"})

@api_view(['POST'])
def register(request):
    user = NewUserSerializer(data=request.data, context={'request': request})
    user.is_valid(raise_exception=True)
    user.save()
    return JsonResponse(user.data, status=201)


class RoleBasedModelViewSet(viewsets.ModelViewSet):
    model = None
    def get_queryset(self):
        user = self.request.user
        if user.has_role("ADMIN"):
            return self.model.objects.all()
        else:
            return self.model.objects.filter(user_id=user.id)


class UserViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = User.objects.all().order_by('id')
    serializer_class = UserSerializer

    def retrieve_user(self, request, *args, **kwargs):
        self.kwargs["pk"] = request.user.id
        return self.retrieve(request, *args, **kwargs)


class VideoViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, mixins.RetrieveModelMixin,
                     viewsets.GenericViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Video.objects.all().order_by('-created_at')
    serializer_class = VideoSerializer
    filter_backends = (DjangoFilterBackend, OrderingFilter,)
    # filter_fields = ('',)
    ordering_fields = ('id', 'created_at',)
    ordering = ('-created_at',)

    def get_queryset(self):
        if self.action == 'list' or self.action == 'retrieve':
            return self.queryset
        return self.queryset.filter(user_id=self.request.user.id)

    @detail_route(methods=['get'])
    def comments(self,request,pk=None):
        try:
            queryset = Comment.objects.filter(video_id=pk).order_by("-created_at")
            page = self.paginate_queryset(queryset)
            if page is not None:
                serializer = CommentSerializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            serializer = CommentSerializer(queryset, many=True)
            return Response(serializer.data)
        except:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

class CommentViewSet( mixins.ListModelMixin, mixins.CreateModelMixin, mixins.RetrieveModelMixin,
                     viewsets.GenericViewSet):
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Comment.objects.all().order_by('-created_at')
    serializer_class = CommentSerializer
    filter_backends = (DjangoFilterBackend, OrderingFilter,)
    filter_fields = ('video','user',)
    ordering_fields = ('id', 'created_at',)
    ordering = ('-created_at',)

    # def get_queryset(self):
    #     return Comment.objects.filter(user_id=self.request.user.id)
