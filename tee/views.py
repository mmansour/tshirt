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

class TShirtForm(forms.Form):
    logo = forms.ImageField(required=True, validators=[validate_file_extension])
    additional_notes = forms.CharField(widget=forms.Textarea, required=False,)


#TO avoid duplicated entries: see "if created"
@receiver(post_save, sender=User, dispatch_uid='views')
def user_created(sender, instance, created, **kwargs):
    if created:
        print("User Added")

        
#UPON SHIRT CREATION OR UPDATE SEND AN EMAIL TO RODEO and CREATOR
@receiver(post_save, sender=TShirt, dispatch_uid='views')
def shirt_created(sender, instance, created, **kwargs):
    if created:
        #TO Rodeo
        subject = 'New shirt created by {0} {1}'.format(instance.user.first_name, instance.user.last_name)
        text_content = '{0} {1} has created a shirt. Order # {2}'.format(instance.user.first_name, instance.user.last_name, instance.id)
        html_content = '{0} {1} has created a shirt. <a href="http://request.rodeoarcade.com/admin/" target="_blank">Order # {2}</a>'.format(instance.user.first_name, instance.user.last_name, instance.id)

        creator_subject = "Your design has been uploaded"
        creator_text_content = "Your design has been uploaded."
        creator_html_content = "Your design has been uploaded."

    else:
        #TO Rodeo
        subject = 'Shirt edited by {0} {1}'.format(instance.user.first_name, instance.user.last_name)
        text_content = '{0} {1} has edited a shirt. Order # {2}'.format(instance.user.first_name, instance.user.last_name, instance.id)
        html_content = '{0} {1} has edited a shirt. <a href="http://request.rodeoarcade.com/admin/" target="_blank">Order # {2}</a>'.format(instance.user.first_name, instance.user.last_name, instance.id)

        creator_subject = "Your design has been edited"
        creator_text_content = "Your design has been edited."
        creator_html_content = "Your design has been edited."

    from_email='matt.mansour@makerstudios.com'
    to='slackbabbath@gmail.com'
    creater_to = instance.user.email

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
#        return HttpResponse('Page Edited')
    return HttpResponse('Edit Page')


def success(request):
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
        'additional_notes':tshirt.additional_instructions,
        'logo':"",
    }

    form = TShirtForm(auto_id=True, initial=init_data)
    if request.method == "POST":
        form = TShirtForm(request.POST, request.FILES, auto_id=True)
        if form.is_valid():
            logo = form.cleaned_data['logo']
            additional_instructions = form.cleaned_data['additional_notes']

            if not logo:
                tshirt.logo = init_data['logo']
            else:
                tshirt.logo = logo
            tshirt.additional_instructions = additional_instructions
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

    form = TShirtForm(auto_id=True)
    if request.method == "POST":
        form = TShirtForm(request.POST, request.FILES, auto_id=True)

        if form.is_valid():
            logo = form.cleaned_data['logo']
            additional_instructions = form.cleaned_data['additional_notes']

            obj = TShirt(title='Order from site',
                         user=request.user,
                         logo=logo,
                         additional_instructions=additional_instructions,
                         is_order_closed=False)
            obj.save()

            redirect = "/designer/?logo={0}&shirtid={1}".format(obj.logo, obj.id)
            return HttpResponseRedirect(redirect)

    return render_to_response('pages/create-tshirt.html',
                   {'form':form},
                    context_instance=RequestContext(request))


