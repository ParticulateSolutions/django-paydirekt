from django.conf.urls import include, url

urlpatterns = [
    url('^paydirekt/', include('django_paydirekt.urls')),
]
