from django_paydirekt import settings as django_paydirekt_settings


def build_paydirekt_full_uri(url):
    if url.startswith('/'):
        url = '{0}{1}'.format(django_paydirekt_settings.PAYDIREKT_ROOT_URL, url)
    return url
