import sys

import django
from django.conf import settings
from django.test.utils import get_runner


def main():
    # configure django settings with test settings
    from tests import settings as test_settings

    django.setup()
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(['tests'])
    sys.exit(failures)


if __name__ == '__main__':
    main()