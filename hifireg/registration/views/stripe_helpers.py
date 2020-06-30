from django.conf import settings

import stripe


def create_stripe_checkout_session(amount, success_url, cancel_url):
    """
    Create a new Stripe checkout session and return the session id.
    """
    # configure Stripe w/secret API key
    stripe.api_key = settings.STRIPE_SECRET_TEST_KEY

    # Create new Checkout Session for the order
    # Other optional params: https:#stripe.com/docs/api/checkout/sessions/create
    checkout_session = stripe.checkout.Session.create(
        success_url = success_url,
        cancel_url = cancel_url,
        payment_method_types = ['card'],
        line_items = [{
            'price_data': {
                'currency': 'usd',
                'product_data': {
                    'name': 'HiFi Registration',
                },
                'unit_amount': amount,
            },
            'quantity': 1,
        }],
        mode = 'payment',
    )
    return checkout_session['id']


def get_stripe_checkout_session_total(checkout_session_id):
    """
    Get the total amount paid for a Stripe checkout session.
    """
    stripe.api_key = settings.STRIPE_SECRET_TEST_KEY
    line_items = stripe.checkout.Session.list_line_items(checkout_session_id)
    total_amount = 0
    for line_item in line_items['data']:
        total_amount += line_item['amount_total']
    return total_amount