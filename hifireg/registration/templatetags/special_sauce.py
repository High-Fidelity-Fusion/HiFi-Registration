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


@register.filter
def dollars(value):
    return f"${value * 0.01:.2f}"


@register.filter
def add_class(field, css_class):
    return field.as_widget(attrs={"class":css_class})
