from django.conf.urls import url
from django.conf.urls.static import static
from django.conf import settings
from . import views

# Create your urls below
urlpatterns = [
    url(r"post_plant/", views.PostListPlantsApiView.as_view()),
    url(r"list_plants/", views.ListPlantsApiView.as_view()),
    url(r"update_delete_plant/(?P<plant_id>[0-9a-f-]+)/", views.RetreiveUpdateDeletePlantsApiView.as_view()),
    url(r"add_update_get_cart/", views.AddGetCartApiView.as_view()),
    url(r"delete_cart/(?P<cart_id>[0-9a-f-]+)/", views.DeleteCartApiView.as_view()),
    url(r"place_order/", views.AddGetOrderApiView.as_view()),
    url(r"view_received_order/", views.NurseryViewOrdersApiView.as_view()),
    url(r"update_order_status/(?P<order_id>[0-9a-f-]+)/", views.UpdateOrderStatusApiView.as_view()),
]
