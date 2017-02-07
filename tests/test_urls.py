from django.conf.urls import include, url

urlpatterns = [
    url('^paydirekt/', include('django_paydirekt.urls', namespace='paydirekt', app_name='paydirekt')),
]
