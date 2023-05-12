from rest_framework import mixins, viewsets


class BaseListCreateDestroyView(mixins.DestroyModelMixin,
                                mixins.ListModelMixin,
                                mixins.CreateModelMixin,
                                viewsets.GenericViewSet
                                ):
    lookup_field = 'slug'
