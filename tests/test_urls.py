from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url('^paydirekt/', include('django_paydirekt.urls', namespace='paydirekt', app_name='paydirekt')),
)
