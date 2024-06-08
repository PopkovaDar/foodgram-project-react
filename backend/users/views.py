from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from foodgram.pagination import Pagination
from users.models import FollowUser, User
from users.serializers import (FollowSerializer, FollowUserSerializer,
                               UserSerializer)


class UserViewSet(UserViewSet):
    """Создание пользователей."""
    pagination_class = Pagination

    @action(
        detail=False,
        methods=['GET', 'PATCH'],
        url_path='me',
        permission_classes=[IsAuthenticated],
    )
    def me(self, request):
        """Текущий пользователь."""
        serializer = UserSerializer(request.user, context={'request': request})
        if request.method == 'GET':
            return Response(serializer.data, status=status.HTTP_200_OK)
        serializer = UserSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        methods=['POST', 'DELETE'],
        detail=True,
        permission_classes=[IsAuthenticated, ],)
    def subscribe(self, request, id):
        """Подписка или отписка от автора."""
        author = get_object_or_404(User, id=id)
        user = request.user
        data = {'author': author.id,
                'user': user.id}
        if request.method == 'POST':
            serializer = FollowSerializer(data=data,
                                          context={'request': request,
                                                   'pk': id})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            subscription = FollowUser.objects.filter(
                author=author.id,
                user=user.id)
            if not subscription:
                return Response({'errors': "Подписка не найдена!"},
                                status=status.HTTP_400_BAD_REQUEST)
            if subscription:
                subscription.delete()
                return Response(
                    subscription,
                    status=status.HTTP_204_NO_CONTENT
                )
            return Response({'errors': "Вы не подписаны на данного автора!"},
                            status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=False,
        methods=['GET'],
        permission_classes=[IsAuthenticated],
    )
    def subscriptions(self, request):
        """Подписки пользователя."""
        paginate_queryset = self.paginate_queryset(
            FollowUser.objects.filter(user=request.user)
        )
        serializer = FollowUserSerializer(
            paginate_queryset,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)
