from django.conf.urls.defaults import *
from django.contrib import admin
admin.autodiscover()

from mezzanine.core.views import direct_to_template

urlpatterns = patterns('tee.views',
#    url("^$", "home", name="home"),
    (r'^create-tshirt/$', 'create_shirt_form'),
    (r'^my-tshirts/$', 'my_shirt_list'),
    (r'^my-tshirts/edit/(?P<shirt_id>\d+)/$', 'edit_shirt'),
)
  