from django.contrib.sessions.models import Session
from django.conf import settings
from django.db import models
from django.db.models import F
from .comp_code import CompCode

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

    @classmethod
    def for_user(cls, user):
        return cls.objects.get(user=user)


class Volunteer(models.Model):
    registration = models.OneToOneField(Registration, on_delete=models.CASCADE, null=True, blank=True)
    cellphone_number = models.CharField(verbose_name='Cell Phone Number', max_length=30, null=True, blank=True)
    hours_max = models.IntegerField(verbose_name='How many hours are you willing to Contribute?', null=True, blank=True)
    image = models.ImageField(upload_to='2020/volunteers/', verbose_name='Please upload an image of your face', help_text='We need to know what you look like so we know who to look for!', null=True, blank=True)
    skills = models.TextField(verbose_name="How can we best utilize your skills?", help_text="Are you particularly talented at something? Do you have a strong preference toward helping in a particular way? We would like to know more!", null=True, blank=True)
    cantwont = models.TextField(verbose_name="What can't/won't you do?", help_text="You can't lift heavy things? Garbage evokes nausea in you? You are afraid of spiders? These are things we want to know! We don't want to ask you to do anything that does not suit you.", null=True, blank=True)

