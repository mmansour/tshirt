from django.db import models
from mezzanine.core.models import Displayable, RichTextField
from mezzanine.generic.fields import CommentsField, RatingField
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.db.models.signals import post_save

class TShirt(Displayable):

    user = models.ForeignKey(User)
    shirt_text = models.CharField(max_length=400, verbose_name="Text", blank=True, null=True)
    logo = models.ImageField(upload_to="uploads", blank=True, null=True, default='uploads/25off.png')
    design_layout = models.ImageField(upload_to="uploads", blank=True, null=True, default='uploads/25off.png')
    color = models.CharField(max_length=400, verbose_name="Shirt Color", blank=True)
    additional_instructions = models.TextField(verbose_name="Additional Instructions", blank=True)
    is_order_closed = models.BooleanField(blank=True, verbose_name="Order Closed?", default=False)

    def __unicode__(self):
        return self.title





