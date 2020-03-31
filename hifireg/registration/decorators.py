from .models.registration import Registration, Order, OrderItem
from django.shortcuts import redirect

def must_have_registration(function):
    def wrap(request, *args, **kwargs):
        if Registration.objects.filter(user=request.user).exists():
            return function(request, *args, **kwargs)
        else:
            return redirect('register-comp-code')
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap

def must_have_order(function):
    @must_have_registration
    def wrap(request, *args, **kwargs):
        order = Order.objects.filter(registration__user=request.user, session__isnull=False).count()
        if OrderItem.objects.filter(order__registration__user=request.user, order__session__isnull=False).exists():
            return function(request, *args, **kwargs)
        else:
            return redirect('register-ticket-selection')
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap