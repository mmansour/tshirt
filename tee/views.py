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


def validate_file_extension(value):
    if not value.name.endswith('.png'):
        raise ValidationError(u'Image must be a .png.')

class TShirtForm(forms.Form):
    logo = forms.ImageField(required=False, validators=[validate_file_extension])
    additional_instructions = forms.CharField(widget=forms.Textarea, required=False)


def unauthorized(request):
    return render_to_response('pages/unauthorized.html',
               {},
                context_instance=RequestContext(request))


def designer(request):
    return render_to_response('pages/designer.html',
               {},
                context_instance=RequestContext(request))


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

            redirect = "/designer/?logo={0}".format(tshirt.logo)
            return HttpResponseRedirect(redirect)

    return render_to_response('pages/edit-tshirt.html',
               {'tshirt':tshirt,'form':form},
                context_instance=RequestContext(request))


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
            additional_instructions = form.cleaned_data['additional_instructions']

            obj = TShirt(title='Order from site',
                         user=request.user,
                         logo=logo,
                         additional_instructions=additional_instructions,
                         is_order_closed=False)
            obj.save()

            redirect = "/designer/?logo={0}".format(obj.logo)
            return HttpResponseRedirect(redirect)

    return render_to_response('pages/create-tshirt.html',
                   {'form':form},
                    context_instance=RequestContext(request))


