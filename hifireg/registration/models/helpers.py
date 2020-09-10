from django.db.models import F, Sum, OuterRef, Subquery, Case, Value, When, BooleanField
from django.db.models.functions import Coalesce
from .payment import Payment
from .invoice import Invoice

def with_is_paid(invoiceQuerySet):
    pay_at_checkout_invoices = Invoice.objects.filter(order__registration=OuterRef('order__registration__pk'), pay_at_checkout=True, order__session__isnull=True).exclude(pk=OuterRef('pk')).order_by().values('order__registration').annotate(sum=Sum('amount')).values('sum')
    prior_pay_later_invoices = Invoice.objects.filter(order__registration=OuterRef('order__registration__pk'), pay_at_checkout=False, order__session__isnull=True, due_date__lte=OuterRef('due_date')).exclude(pk=OuterRef('pk')).order_by().values('order__registration').annotate(sum=Sum('amount')).values('sum')
    payments = Payment.objects.filter(registration=OuterRef('order__registration__pk')).order_by().values('registration').annotate(sum=Sum('amount')).values('sum')

    return invoiceQuerySet.filter(order__session__isnull=True).order_by('due_date').annotate(pay_at_checkout_invoices=Coalesce(Subquery(pay_at_checkout_invoices), 0)). \
        annotate(prior_pay_later_invoices=Case(When(pay_at_checkout=False, then=Coalesce(Subquery(prior_pay_later_invoices), 0)), default=Value(0))). \
        annotate(sum_of_payments=Coalesce(Subquery(payments), 0)). \
        annotate(unpaid_amount_through_this=F('pay_at_checkout_invoices') + F('prior_pay_later_invoices') + F('amount') - F('sum_of_payments')). \
        annotate(unpaid_amount=Case(When(unpaid_amount_through_this__gte=F('amount'), then='amount'), When(unpaid_amount_through_this__lte=Value(0), then=Value(0)), default=F('unpaid_amount_through_this'))). \
        annotate(is_paid=Case(When(unpaid_amount__gt=Value(0), then=Value(False)), default=Value(True), output_field=BooleanField()))

