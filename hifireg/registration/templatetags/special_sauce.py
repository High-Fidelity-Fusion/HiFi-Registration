from django import template
from registration.views.utils import LinkButton, SubmitButton


register = template.Library()


@register.filter
def is_link(value):
    return isinstance(value, LinkButton)


@register.filter
def is_submit(value):
    return isinstance(value, SubmitButton)


@register.filter
def eq(value, arg):
    return value == arg


@register.inclusion_tag('utils/form_control.html')
def form_control(value):
    return {'button': value}


@register.inclusion_tag('utils/button.html')
def button(value):
    return {'button': value}
