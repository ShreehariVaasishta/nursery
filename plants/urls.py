from django.conf.urls import url
from django.conf.urls.static import static
from django.conf import settings
from . import views

# Create your urls below
urlpatterns = [
    url(r"post_plant/", views.PostListPlantsApiView.as_view()),
    url(r"list_plants/", views.ListPlantsApiView.as_view()),
    url(r"update_delete_plant/(?P<plant_id>[0-9a-f-]+)/", views.UpdateDeletePlantsApiView.as_view()),
]
