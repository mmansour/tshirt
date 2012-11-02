from tee.models import TShirt
from django.contrib import admin
from mezzanine.core.admin import DisplayableAdmin


class TShirtAdmin(DisplayableAdmin):

    fieldsets = [
        ("Title",                       {'fields': ['title']}),
        ("Published Date",              {'fields': ['publish_date']}),
        ("Published Status",            {'fields': ['status']}),
        ("Order Closed?",            {'fields': ['is_order_closed']}),
        ("User",            {'fields': ['user']}),
        ("Logo",            {'fields': ['logo',]}),
        ("Color",            {'fields': ['color',]}),
        ("Additional Instructions",            {'fields': ['additional_instructions',]}),
    ]

    def logo_link(self,obj):
        return u'<a href="/static/media/%s/">%s</a>' % (obj.logo, obj.logo)
    logo_link.allow_tags = True

    list_display = ('user','title', 'logo_link','color' ,'additional_instructions' ,'publish_date', 'is_order_closed',)
    list_display_links = ('user',)
    list_editable = ('is_order_closed',)
    list_filter = ['user','is_order_closed', 'publish_date',]
    search_fields = ['title',]
    date_hierarchy = 'publish_date'

admin.site.register(TShirt, TShirtAdmin)
  