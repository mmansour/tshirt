from tee.models import TShirt, AllowedUser
from django.contrib.auth.models import User

from django.shortcuts import render_to_response, get_object_or_404, get_list_or_404
from django.template import RequestContext
from django import forms
from django.http import HttpResponse, Http404, HttpResponsePermanentRedirect, HttpResponseRedirect

from django.db.models.signals import post_save
from django.dispatch import receiver

from django.core.mail import EmailMultiAlternatives
from django.core.exceptions import ValidationError
from django.views.decorators.csrf import csrf_exempt,  csrf_protect
import os


def validate_file_extension(value): # add to logo field to activate: validators=[validate_file_extension]
    if not value.name.endswith('.png'):
        raise ValidationError(u'Image must be a .png.')
#    if value.name.endswith('.jpeg'):
#        value.name.replace('.jpeg', '.jpg')

SIZES = (
    ('Size', 'Size'),
    ('Small', 'Small'),
    ('Medium', 'Medium'),
    ('Large', 'Large'),
    ('XLarge', 'XLarge'),
    ('2XLarge', '2XLarge'),
    ('3XLarge', '3XLarge'),
)

class TShirtLogo(forms.Form):
    logo = forms.ImageField(required=True, validators=[validate_file_extension])


class TShirtInstructions(forms.Form):
    name_of_shirt = forms.CharField(required=True,)
    size = forms.ChoiceField(choices=SIZES)
#    color = forms.HiddenInput()
    additional_notes = forms.CharField(widget=forms.Textarea, required=False,)


# New Email Function
def email_shirt_created(request, order_id):
    #TO Rodeo
    subject = 'New shirt created by {0} {1}'.format(request.user.first_name, request.user.last_name)
    text_content = '{0} {1} has created a shirt. Order # {2}'.format(request.user.first_name, request.user.last_name, order_id)
    html_content = '{0} {1} has created a shirt. <a href="http://request.rodeoarcade.com/admin/" target="_blank">Order # {2}</a>'.format(request.user.first_name, request.user.last_name, order_id)

    creator_subject = "Your design has been uploaded"
    creator_text_content = "Your design has been uploaded."
    creator_html_content = "Your design has been uploaded."

    from_email='matt.mansour@makerstudios.com'
    to='slackbabbath@gmail.com'
    creater_to = request.user.email

    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
    msg.attach_alternative(html_content, "text/html")
    msg.send()

    creator_msg = EmailMultiAlternatives(creator_subject, creator_text_content, from_email, [creater_to])
    creator_msg.attach_alternative(creator_html_content, "text/html")
    creator_msg.send()

        
def tool_edit(request, shirt_id):
    try:
        is_in_list = AllowedUser.objects.get(email_address=request.user.email)
        print 'Found authorized user email: %s' % is_in_list.email_address
    except AllowedUser.DoesNotExist:
        print 'User not allowed'
        return HttpResponseRedirect('/forbidden/')

    tshirt = TShirt.objects.get(id=shirt_id)

    if request.method == "POST":
        logo = request.body
        imagename = str(tshirt.logo.url)
        image_url_path = imagename[:22]
        image_file_name = imagename[22:]
        new_logo_filename = "{0}-{1}".format(tshirt.id, image_file_name)
        new_upload_path = "{0}{1}".format(image_url_path, new_logo_filename)
        curpath = os.path.abspath(os.curdir)
        out = open('{0}{1}'.format(curpath, new_upload_path), 'wb+')
        out.write(logo)
        out.close()
        tshirt.logo = new_upload_path[14:]
        tshirt.save()
        return HttpResponse('Edited')
    return HttpResponse('Edit Page')


def preview(request, shirt_id):
    try:
        is_in_list = AllowedUser.objects.get(email_address=request.user.email)
        print 'Found authorized user email: %s' % is_in_list.email_address
    except AllowedUser.DoesNotExist:
        print 'User not allowed'
        return HttpResponseRedirect('/forbidden/')

    tshirt = TShirt.objects.get(id=shirt_id)

    if request.user != tshirt.user:
        return HttpResponseRedirect('/forbidden/')

    init_data = {
        'name_of_shirt':tshirt.title,
        'size':tshirt.size,
        'additional_notes':tshirt.additional_instructions,
    }

    form = TShirtInstructions(auto_id=True, initial=init_data)
    if request.method == "POST":
        if request.POST.get('prevcolor', False):
            newcolor = request.POST.get('prevcolor', False)
            tshirt.color = newcolor
            tshirt.save()
            
        form = TShirtInstructions(request.POST, auto_id=True)
        if form.is_valid():
            tshirt.title = form.cleaned_data['name_of_shirt']
            tshirt.size = form.cleaned_data['size']
            tshirt.order_submission_status = "Submitted"
            tshirt.additional_instructions = form.cleaned_data['additional_notes']
            tshirt.save()

            redirect = "/success/{0}/".format(tshirt.id)
            return HttpResponseRedirect(redirect)

    else:
        tshirt.color = request.GET.get('col', 'white')
        tshirt.save()
        
    return render_to_response('pages/preview.html',{'tshirt':tshirt, 'form':form},
                context_instance=RequestContext(request))


@csrf_protect
def success(request, shirt_id):
    try:
        is_in_list = AllowedUser.objects.get(email_address=request.user.email)
        print 'Found authorized user email: %s' % is_in_list.email_address
    except AllowedUser.DoesNotExist:
        print 'User not allowed'
        return HttpResponseRedirect('/forbidden/')

    tshirt = TShirt.objects.get(id=shirt_id)

    if request.user != tshirt.user:
        return HttpResponseRedirect('/forbidden/')

    email_shirt_created(request, tshirt.id)
    
    return render_to_response('pages/success.html',{},
                context_instance=RequestContext(request))


@csrf_protect
def my_shirt_list(request):
    try:
        is_in_list = AllowedUser.objects.get(email_address=request.user.email)
        print 'Found authorized user email: %s' % is_in_list.email_address
    except AllowedUser.DoesNotExist:
        print 'User not allowed'
        return HttpResponseRedirect('/forbidden/')

    shirt_list = TShirt.objects.filter(user=request.user)
    return render_to_response('pages/my-tshirts.html',
               {'shirt_list':shirt_list},
                context_instance=RequestContext(request))


@csrf_protect
def unauthorized(request):
    return render_to_response('pages/unauthorized.html',{},
                context_instance=RequestContext(request))


@csrf_protect
def designer(request):
    if not request.user.is_authenticated():
        return HttpResponseRedirect('/')
    return render_to_response('pages/designer.html',{},
                context_instance=RequestContext(request))


@csrf_protect
def home(request):
    return render_to_response('index.html',{},
                context_instance=RequestContext(request))


@csrf_protect
def edit_shirt(request, shirt_id):
    try:
        is_in_list = AllowedUser.objects.get(email_address=request.user.email)
        print 'Found authorized user email: %s' % is_in_list.email_address
    except AllowedUser.DoesNotExist:
        print 'User not allowed'
        return HttpResponseRedirect('/forbidden/')

    tshirt = TShirt.objects.get(id=shirt_id)

    if request.user != tshirt.user:
        redirect = "/forbidden/"
        return HttpResponseRedirect(redirect)

    init_data = {
        'logo':"",
    }

    form = TShirtLogo(auto_id=True, initial=init_data)
    if request.method == "POST":
        form = TShirtLogo(request.POST, request.FILES, auto_id=True)
        if form.is_valid():
            logo = form.cleaned_data['logo']

            if not logo:
                tshirt.logo = init_data['logo']
            else:
                tshirt.logo = logo
            tshirt.save()

            redirect = "/designer/?logo={0}&shirtid={1}".format(tshirt.logo, tshirt.id)
            return HttpResponseRedirect(redirect)

    return render_to_response('pages/edit-tshirt.html',
               {'tshirt':tshirt,'form':form},
                context_instance=RequestContext(request))


@csrf_protect
def create_shirt_form(request):
    try:
        is_in_list = AllowedUser.objects.get(email_address=request.user.email)
        print 'Found authorized user email: %s' % is_in_list.email_address
    except AllowedUser.DoesNotExist:
        print 'User not allowed'
        return HttpResponseRedirect('/forbidden/')

    form = TShirtLogo(auto_id=True)
    if request.method == "POST":
        form = TShirtLogo(request.POST, request.FILES, auto_id=True)

        if form.is_valid():
            logo = form.cleaned_data['logo']

            obj = TShirt(title='Order from site',
                         user=request.user,
                         logo=logo,
                         order_submission_status = "Started",
                         is_order_closed=False)
            obj.save()

            redirect = "/designer/?logo={0}&shirtid={1}".format(obj.logo, obj.id)
            return HttpResponseRedirect(redirect)

    return render_to_response('pages/create-tshirt.html',
                   {'form':form},
                    context_instance=RequestContext(request))


