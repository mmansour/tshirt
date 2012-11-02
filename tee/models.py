from django.db import models
from mezzanine.core.models import Displayable, RichTextField
from mezzanine.generic.fields import CommentsField, RatingField
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.db.models.signals import post_save

class TShirt(Displayable):

    user = models.ForeignKey(User)
    logo = models.ImageField(upload_to="uploads", blank=True, null=True, default='uploads/25off.png')
    color = models.CharField(max_length=400, verbose_name="Shirt Color", blank=True)
    additional_instructions = models.TextField(verbose_name="Description", blank=True)
    is_order_closed = models.BooleanField(blank=True, verbose_name="Order Closed?", default=False)

#    def save(self, *args, **kwargs):
#        self.title = "Order {0}".format(self.id)
#        super(TShirt, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.title


#    subject_one = models.CharField(max_length=400, verbose_name="First Subject", blank=True)
#    subject_two = models.CharField(max_length=400, verbose_name="Second Subject", blank=True)
#
#    summary = models.TextField(blank=True, verbose_name="Summary of the Diff")
#
#    subject_one_data = models.TextField(blank=True, verbose_name="Subject One Data")
#    subject_two_data = models.TextField(blank=True, verbose_name="Subject Two Data")
#
#    subject_one_video = models.TextField(blank=True, verbose_name="Subject One Video")
#    subject_two_video = models.TextField(blank=True, verbose_name="Subject Two Video")
#
#    subject_one_ad = models.TextField(blank=True, verbose_name="Subject One Ad")
#    subject_two_ad = models.TextField(blank=True, verbose_name="Subject Two Ad")
#
#    subject_one_data_dictservice = models.TextField(blank=True, verbose_name="Subject One Data DictService")
#    subject_two_data_dictservice = models.TextField(blank=True, verbose_name="Subject Two Data DictService")
#
#    subject_data_sources = models.TextField(blank=True, verbose_name="Data Sources")
#
#    allow_comments = models.BooleanField(default=True)
#    is_title_case = models.BooleanField(default=True)
#    comments = CommentsField(verbose_name=_("Comments"))
#    rating = RatingField(verbose_name=_("Rating"))

#    @models.permalink
#    def get_absolute_url(self):
#        return ('tshirt.tee.views.what_is', [self.slug,])





