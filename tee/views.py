from tee.models import *
from django.shortcuts import render_to_response, get_object_or_404, get_list_or_404
from django.template import RequestContext
from django.http import HttpResponse, Http404, HttpResponsePermanentRedirect



def create_shirt_form(request):
    return render_to_response('pages/create-tshirt.html',
                       {},
                        context_instance=RequestContext(request))
