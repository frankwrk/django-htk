# Python Standard Library Imports

# Third Party / PIP Imports

# Django Imports
from django.conf import settings

# HTK Imports


def run_task_async_or_immediately_per_env(task_fn):
    if settings.TEST or settings.ENV_DEV:
        # invoke immediately for test and dev
        task_fn()
    else:
        # invoke asynchronously for prod
        task_fn.delay()
