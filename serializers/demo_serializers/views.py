from rest_framework.generics import GenericAPIView
from rest_framework import mixins, views, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters import rest_framework
from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from .serializers import *
from rest_framework.exceptions import ValidationError


class ItemDetailView(mixins.RetrieveModelMixin,
                    mixins.UpdateModelMixin,
                    mixins.DestroyModelMixin,
                    generics.GenericAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemDisplaySerializer

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class ItemListFilter(rest_framework.FilterSet):
    name = rest_framework.CharFilter(
        label="name",
        field_name="name",
        lookup_expr='icontains'
    )
    archive_status = rest_framework.BooleanFilter(
        label="archive_status",
        field_name="archive_status"
    )
    good_rating_filter = rest_framework.BooleanFilter(
        label="good_rating_filter",
        method="filter_good_restaurants"
    )

    def filter_good_restaurants(self, queryset, name, value):
        if value:
            queryset = queryset.filter(Q(rating__gte=3) & Q(rating__lte=5))
        return queryset


class ItemListView(generics.ListCreateAPIView):
    filterset_class = ItemListFilter
    queryset = Item.objects.all()
    serializer_class = ItemDisplaySerializer

    def get_serializer_context(self):  # Things can be passed to stop DB queries
        return {
            'current_user': self.request.user.id
        }

    def view_context(self):  # Sometimes a good practice to put in common logic here
        return {
            'current_user': self.request.user.id
        }

    def get(self, request, *args, **kwargs):
        pass  # self.view_context().get('current_user')
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


from rest_framework.pagination import PageNumberPagination


class SmallResultsSetPagination(PageNumberPagination):
    page_size = 2
    page_size_query_param = 'page_size'
    max_page_size = 2


class SmallItemListView(generics.ListAPIView):
    pagination_class = SmallResultsSetPagination
    queryset = Item.objects.all()
    serializer_class = ItemDisplaySerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class ItemActionView(views.APIView):
    def view_context(self, *args, **kwargs):  # Sometimes a good practice to put in common logic here
        item = Item.objects.get(id=kwargs.get("pk"))
        return {
            "item": item
        }

    def get(self, request, *args, **kwargs):
        view_context = self.view_context(*args, **kwargs)
        item = view_context.get("item")
        return Response({"id": item.id})

    def post(self, request, *args, **kwargs):
        view_context = self.view_context(*args, **kwargs)
        item = view_context.get("item")

        serializer = ItemArchiveSerializer(data=request.data)
        if serializer.is_valid():
            item.archive = False
            item.save()
            return Response({"id": item.id})
        else:
            return Response(serializer.errors)
