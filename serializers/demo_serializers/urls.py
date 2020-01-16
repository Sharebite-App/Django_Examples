from django.conf.urls import url
from api.v1.demo_serializers.views import *
from api.v1.corporates.views import *

urlpatterns = [
    url(r'^item/(?P<pk>[0-9]+)/', ItemDetailView.as_view()),
    url(r'^item/', ItemListView.as_view()),
    url(r'^item_small/', SmallItemListView.as_view()),
    url(r'^item_action/(?P<pk>[0-9]+)/', ItemActionView.as_view()),
]
