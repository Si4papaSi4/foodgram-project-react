from rest_framework import mixins, viewsets
from rest_framework.response import Response


class CreateListDestroyMixin(viewsets.GenericViewSet,
                             mixins.CreateModelMixin,
                             mixins.ListModelMixin,
                             mixins.DestroyModelMixin):
    """
    Миксин для методов POST, GET(LIST), DELETE.
    """


class PatchModelMixin(mixins.UpdateModelMixin):
    """
    Миксин для метода PATCH.
    """

    def update(self, request, *args, **kwargs):
        """
        Кастомная функция update, исключающая PUT метод.
        """
        partial = False
        instance = self.get_object()
        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=partial
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)


class NoPatchMixin(CreateListDestroyMixin,
                   PatchModelMixin,
                   mixins.RetrieveModelMixin):
    pass
