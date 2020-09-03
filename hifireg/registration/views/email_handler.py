from django.core.mail import EmailMessage
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.views import View

from hifireg import settings

from .mixins import RegistrationRequiredMixin, OrderRequiredMixin


def send_confirmation(user, order):
    items = order.orderitem_set.order_by('product__category__section', 'product__category__rank', 'product__slots__rank')

    context = dict(user=user, order=order, items=items)

    subject = "Thank you for you order!"
    text_content = render_to_string('email/order.txt', context)
    html_content= render_to_string('email/order.html', context)

    msg = EmailMultiAlternatives()
    msg.to = [user.email]
    msg.subject = subject
    msg.body = text_content
    msg.attach_alternative(html_content, "text/html")

    try:
        confirmation_email_enabled = settings.CONFIRMATION_EMAIL_ENABLED
    except AttributeError:
        confirmation_email_enabled = True

    if confirmation_email_enabled:
        msg.send(fail_silently=False)

    # return html_content # For debugging
    return text_content # For debugging


class SendEmail(OrderRequiredMixin, View):
    def get(self, request):
        html_content = send_confirmation(request.user, self.order)

        from django.http import HttpResponse
        return HttpResponse(html_content)
