from django.conf.urls import url

from .views import NotifyPaydirektView

urlpatterns = [
    url(r'^notify/$', NotifyPaydirektView.as_view(), name='notifiy'),
]
