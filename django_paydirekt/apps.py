from django.apps.config import AppConfig
from django.utils.translation import gettext_lazy as _


class PaydirektConfig(AppConfig):

    name = 'django_paydirekt'
    verbose_name = _('Django Paydirekt')
