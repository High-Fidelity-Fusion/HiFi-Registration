from django.contrib.sessions.models import Session
from django.conf import settings
from django.core.exceptions import SuspiciousOperation
from django.db import models
from django.db import transaction
from django.db.models import Sum, F

from .comp_code import CompCode


class UserSession(models.Model):
    DjangoSession = models.ForeignKey(Session, on_delete=models.CASCADE, null=True)

    @classmethod
    def get_current_id(cls):
        if UserSession.get_current() is not None:
            return UserSession.get_current().id
        return None

    @classmethod
    def get_current(cls):
        return UserSession.objects.first() #TODO update to get the actual current UserSession based on the current DjangoSession

class Registration(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    comp_code = models.ForeignKey(CompCode, on_delete=models.PROTECT, null=True, blank=True)
    referral_code = models.CharField(max_length=15, null=True, blank=True)
    agrees_to_policy = models.BooleanField(verbose_name='Do you agree to the Code of Conduct?', null=True, blank=True)
    opts_into_photo_review = models.BooleanField(verbose_name='Do you want to participate in the photo review process?', null=True, blank=True)
    wants_to_volunteer = models.BooleanField(verbose_name='Do you want to volunteer?', null=True, blank=True)
    mailing_list = models.BooleanField(verbose_name="Keep up-to-date with HiFi?", help_text="Would you like us to email you in the future with news about Hi-Fi (not more than once monthly)?", null=True, blank=True)
    registration_feedback = models.TextField(verbose_name='Feedback', help_text='What do you think about our registration process? What can we do better for you next time?', null=True, blank=True)
    housing_transport_acknowledgement = models.BooleanField(verbose_name='Will you attend to your own housing and transportation needs?', null=True, blank=True)
    accommodations = models.TextField(verbose_name='How can we accommodate you?', help_text="Is there anything that you need from us to be able to attend the event (that isn't covered elsewhere in the form? Tell us here!", max_length=1000, null=True, blank=True)

    @property
    def is_submitted(self):
        return self.order_set.filter(session=None).exists()

    @property
    def is_accessible_pricing(self):
        return self.order_set.filter(original_price__gt=F('accessible_price')).exists()

    @property
    def is_comped(self):
        return self.comp_code is not None

class Volunteer(models.Model):
    registration = models.OneToOneField(Registration, on_delete=models.CASCADE, null=True, blank=True)
    cellphone_number = models.CharField(verbose_name='Cell Phone Number', max_length=30, null=True, blank=True)
    hours_max = models.IntegerField(verbose_name='How many hours are you willing to Contribute?', null=True, blank=True)
    image = models.ImageField(upload_to='2020/volunteers/', verbose_name='Please upload an image of your face', help_text='We need to know what you look like so we know who to look for!', null=True, blank=True)
    skills = models.TextField(verbose_name="How can we best utilize your skills?", help_text="Are you particularly talented at something? Do you have a strong preference toward helping in a particular way? We would like to know more!", null=True, blank=True)
    cantwont = models.TextField(verbose_name="What can't/won't you do?", help_text="You can't lift heavy things? Garbage evokes nausea in you? You are afraid of spiders? These are things we want to know! We don't want to ask you to do anything that does not suit you.", null=True, blank=True)


class Order(models.Model):
    session = models.OneToOneField(Session, on_delete=models.CASCADE, null=True)
    registration = models.ForeignKey(Registration, on_delete=models.CASCADE)
    original_price = models.PositiveIntegerField(default=0)
    accessible_price = models.PositiveIntegerField(default=0)

    @property
    def is_submitted(self):
        return self.session is None

    @property
    def is_accessible_pricing(self):
        return self.original_price > self.accessible_price

    @property
    def ap_eligible_amount(self):
        return self.orderitem_set.filter(product__is_ap_eligible=True).aggregate(Sum('total_price'))['total_price__sum'] or 0

    def add_item(self, product, quantity):
        if self.is_submitted:
            raise SuspiciousOperation('You cannot add items to a finalized order.')
        for slot in product.slots.iterator():
            if slot.is_exclusionary == True and self.orderitem_set.exclude(product=product).filter(product__slots=slot).exists():
                raise SuspiciousOperation('You cannot have more than one product in an exclusionary slot.')
        if (self.orderitem_set.get(product=product).quantity if self.orderitem_set.filter(product=product).exists() else 0) + quantity > product.max_quantity_per_reg:
            raise SuspiciousOperation('You cannot exceed the max quantity per registration for that product.')


        with transaction.atomic():
            OrderItem.objects.select_for_update()
            if product.available_quantity >= quantity:
                order_item, created = self.orderitem_set.get_or_create(product = product,
                                                                       defaults={'unit_price': 0 if self.registration.is_comped and product.is_compable else product.price})
                order_item.increment(quantity)

                self.original_price = self.orderitem_set.aggregate(Sum('total_price'))['total_price__sum']
                self.accessible_price = self.original_price
                self.save()
                return True
            return False

    def remove_item(self, product, quantity):
        self.orderitem_set.get(product=product).decrement(quantity)
        self.original_price = self.orderitem_set.aggregate(Sum('total_price'))['total_price__sum'] or 0
        if self.original_price < self.accessible_price:
            self.accessible_price = self.original_price
        self.save()

    @transaction.atomic
    def claim_accessible_pricing(self):
        Order.objects.select_for_update()
        if APFund.get_available_funds() >= self.ap_eligible_amount:
            self.accessible_price = self.original_price - self.ap_eligible_amount
            self.save()
            return True
        return False


class OrderItem(models.Model):
    product = models.ForeignKey('Product', on_delete=models.PROTECT)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    unit_price = models.PositiveIntegerField(null=True)
    total_price = models.PositiveIntegerField(null=True)
    quantity = models.PositiveIntegerField(default=0)

    def increment(self, quantity):
        self.quantity += quantity
        self.total_price = self.unit_price * self.quantity
        self.save()

    def decrement(self, quantity):
        self.quantity -= quantity
        self.total_price = self.unit_price * self.quantity
        self.save()
        if self.quantity < 1:
            self.delete()


class APFund(models.Model):
    contribution = models.PositiveIntegerField(default=0)
    notes = models.CharField(max_length=200)
    last_updated = models.TimeField(auto_now=True)

    @classmethod
    def get_available_funds(cls):
        return (APFund.objects.aggregate(Sum('contribution'))['contribution__sum'] or 0) \
               - (Order.objects.aggregate(disbursed_amount=Sum('original_price') - Sum('accessible_price'))['disbursed_amount'] or 0)



