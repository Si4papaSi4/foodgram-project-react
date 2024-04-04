from api.pagination import CustomPagination
from api.subscriptions.serializers import SubscriptionSerializer
from api.users.serializers import CustomUserSerializer
from djoser.views import UserViewSet
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response


class CustomUserViewSet(UserViewSet):
    serializer_class = CustomUserSerializer

    @action(detail=False, methods=['GET'])
    def subscriptions(self, request):
        subscriptions = request.user.subscriptions.all()
        all_data = SubscriptionSerializer(
            subscriptions,
            context={
                'request': request
            },
            many=True
        ).data
        paginator = CustomPagination()
        page = paginator.paginate_queryset(all_data, request)
        if page is not None:
            return paginator.get_paginated_response(page)
        return Response(all_data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'],
            permission_classes=[permissions.IsAuthenticated])
    def subscribe(self, request, id):
        following = self.get_object()
        data = SubscriptionSerializer(
            following,
            context={
                'request': request,
                'object': following
            }
        ).save()
        return Response(data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def delete_subscribe(self, request, id):
        following = self.get_object()
        SubscriptionSerializer(
            following,
            context={
                'request': request,
                'object': following
            }
        ).destroy()
        return Response(status=status.HTTP_204_NO_CONTENT)
