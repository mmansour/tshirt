from django.conf.urls.defaults import *
from django.contrib import admin
admin.autodiscover()

from mezzanine.core.views import direct_to_template

urlpatterns = patterns('tee.views',
    url("^$", "home", name="home"),
    (r'^success/$', 'success'),
    (r'^create-tshirt/$', 'create_shirt_form'),
    (r'^designer/$', 'designer'),
    (r'^forbidden/$', 'unauthorized'),
    (r'^my-tshirts/$', 'my_shirt_list'),
    (r'^my-tshirts/edit/(?P<shirt_id>\d+)/$', 'edit_shirt'),
    (r'^my-tshirts/tool-edit/(?P<shirt_id>\d+)/$', 'tool_edit'),

#    (r'^my-tshirts/tool-edit/(?P<shirt_id>\d+)/(?P<shirt_color>\w+)/$', 'tool_edit'),
)
  