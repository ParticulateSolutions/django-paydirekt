from django.conf.urls import url

from .views import NotifyPaydirektView

app_name = 'paydirekt'

urlpatterns = [
    url(r'^notify/$', NotifyPaydirektView.as_view(), name='notifiy'),
]
