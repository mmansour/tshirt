from django.db import models
from mezzanine.core.models import Displayable, RichTextField
from mezzanine.generic.fields import CommentsField, RatingField
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User

class TShirt(Displayable):
    user = models.ForeignKey(User)
    shirt_text = models.CharField(max_length=400, verbose_name="Text", blank=True, null=True)
    logo = models.ImageField(upload_to="uploads", blank=True, null=True, default='uploads/25off.png')
    design_layout = models.ImageField(upload_to="uploads", blank=True, null=True, default='uploads/25off.png')
    color = models.CharField(max_length=400, verbose_name="Shirt Color", blank=True)
    additional_instructions = models.TextField(verbose_name="Additional Notes", blank=True)
    is_order_closed = models.BooleanField(blank=True, verbose_name="Order Closed?", default=False)

    def __unicode__(self):
        return self.title


class AllowedUser(models.Model):
    first_name = models.CharField(max_length=40, verbose_name="First Name", blank=True, null=True)
    last_name = models.CharField(max_length=40, verbose_name="Last Name", blank=True, null=True)
    email_address = models.EmailField(blank=True, null=True, verbose_name="Email Address",
            help_text=_('Email address should be the one on record at Maker/RPM/TGS etc..'))

    def __unicode__(self):
        return self.email_address







