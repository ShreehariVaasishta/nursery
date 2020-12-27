from django.conf.urls import url

from . import views

# Create your urls below
urlpatterns = [
    # Buyer
    url(r"register_buyer/", views.BuyerRegisterationApiView.as_view()),
    url(r"login_buyer/", views.BuyerLoginApiView.as_view()),
    url(r"get_update_delete_buyer/", views.BuyerRetreiveUpdateDeleteApiView.as_view()),
    # Nursery
    url(r"register_nursery/", views.NurseryRegisterationApiView.as_view()),
    url(r"login_nursery/", views.NurseryLoginApiView.as_view()),
    url(r"get_update_delete_nursery/", views.NurseryRetreiveUpdateDeleteApiView.as_view()),
]
