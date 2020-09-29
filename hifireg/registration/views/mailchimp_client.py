from mailchimp3 import MailChimp
from mailchimp3.helpers import get_subscriber_hash
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def create_or_update_subscriber(user, registration):
    if (hasattr(settings,'MAILCHIMP_API_KEY')):
        try:
            client = MailChimp(settings.MAILCHIMP_API_KEY, settings.MAILCHIMP_USERNAME)
            hash = get_subscriber_hash(user.email)
            client.lists.members.create_or_update(settings.MAILCHIMP_LIST, hash, {
                'email_address': user.email,
                'status_if_new': 'subscribed',
                'status': 'subscribed',
                'merge_fields': {
                    'FNAME': user.first_name,
                    'LNAME': user.last_name,
                    'STATUS': 'subscribed',
                }
            })
            client.lists.members.tags.update(list_id=settings.MAILCHIMP_LIST, subscriber_hash=hash, data={
                'tags': [
                    {'name': 'AP', 'status': 'active' if registration.is_accessible_pricing else 'inactive'},
                    {'name': 'Volunteer', 'status': 'active' if registration.wants_to_volunteer else 'inactive'},
                    {'name': 'PaymentPlan', 'status': 'active' if registration.is_payment_plan else 'inactive'},
                ]
            })
        except Exception as e:
            logger.error(str(e))

