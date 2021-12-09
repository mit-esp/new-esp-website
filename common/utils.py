from functools import wraps

from django.conf import settings


def csrf_exempt_localhost(view_func):
    """
    Verbatim django's csrf_exempt decorator for localhost only.

    This is necessary if the csrf token cannot be passed to the frontend, which is currently
    true for the scheduler react app.
    """
    def wrapped_view(*args, **kwargs):
        return view_func(*args, **kwargs)
    if settings.LOCALHOST:
        wrapped_view.csrf_exempt = True
    return wraps(view_func)(wrapped_view)
