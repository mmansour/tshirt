from tee.models import TShirt
from django.shortcuts import render_to_response, get_object_or_404, get_list_or_404
from django.template import RequestContext
from django import forms
from django.http import HttpResponse, Http404, HttpResponsePermanentRedirect, HttpResponseRedirect


def my_shirt_list(request):
    shirt_list = TShirt.objects.filter(user=request.user)
#    print request.user.last_name
    return render_to_response('pages/my-tshirts.html',
               {'shirt_list':shirt_list},
                context_instance=RequestContext(request))


class TShirtForm(forms.Form):
    logo = forms.ImageField(required=False)
    additional_instructions = forms.CharField(widget=forms.Textarea, required=False)


def unauthorized(request):

    return render_to_response('pages/unauthorized.html',
               {},
                context_instance=RequestContext(request))



def edit_shirt(request, shirt_id):
    tshirt = TShirt.objects.get(id=shirt_id)

    if request.user != tshirt.user:
        redirect = "/forbidden/"
        return HttpResponseRedirect(redirect)

    init_data = {
        'additional_instructions':tshirt.additional_instructions,
        'logo':tshirt.logo,
    }

    form = TShirtForm(auto_id=True, initial=init_data)
    if request.method == "POST":
        form = TShirtForm(request.POST, request.FILES, auto_id=True)
        if form.is_valid():
            logo = form.cleaned_data['logo']
            additional_instructions = form.cleaned_data['additional_instructions']

            if not logo:
                tshirt.logo = init_data['logo']
            else:
                tshirt.logo = logo
            tshirt.additional_instructions = additional_instructions
            tshirt.save()

            redirect = "{0}?submitted=true".format(request.path)
            return HttpResponseRedirect(redirect)

    return render_to_response('pages/edit-tshirt.html',
               {'tshirt':tshirt,'form':form},
                context_instance=RequestContext(request))


def create_shirt_form(request):
    form = TShirtForm(auto_id=True)
    if request.method == "POST":
        form = TShirtForm(request.POST, request.FILES, auto_id=True)
        if form.is_valid():
            logo = form.cleaned_data['logo']
            additional_instructions = form.cleaned_data['additional_instructions']

            obj = TShirt(title='Order from site',
                         user=request.user,
                         logo=logo,
                         additional_instructions=additional_instructions,
                         is_order_closed=False)
            obj.save()
            
            redirect = "{0}?submitted=true".format(request.path)
            return HttpResponseRedirect(redirect)

    return render_to_response('pages/create-tshirt.html',
                   {'form':form},
                    context_instance=RequestContext(request))


