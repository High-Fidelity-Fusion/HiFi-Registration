from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from functools import wraps

from registration.models import Registration, Order, OrderItem

def must_have_registration(function):
    @login_required
    @wraps(function)
    def wrap(request, *args, **kwargs):
        if Registration.objects.filter(user=request.user).exists():
            return function(request, *args, **kwargs)
        else:
            return redirect('registration')
    # wrap.__doc__ = function.__doc__       made obsolete by @wraps
    # wrap.__name__ = function.__name__     made obsolete by @wraps
    return wrap


def must_have_order(function):
    @must_have_registration
    def wrap(request, *args, **kwargs):
        order = Order.objects.filter(registration__user=request.user, session__isnull=False).count()
        if OrderItem.objects.filter(order__registration__user=request.user, order__session__isnull=False).exists():
            return function(request, *args, **kwargs)
        else:
            return redirect('order')
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap
