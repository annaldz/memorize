from django.shortcuts import render,render_to_response
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.views import password_reset, password_reset_done, password_reset_confirm, password_reset_complete
from users.forms import UserForm,ProfileAlterForm
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.contrib.auth.forms import PasswordChangeForm
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.template.response import TemplateResponse
from files.models import Directory, FileStorage
from users.models import Profile
from django.db import transaction
from django.utils import timezone
from social.apps.django_app.default.models import UserSocialAuth


def user_login(request):
    context = RequestContext(request)

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)

        if user:
            if user.is_active:
                login(request, user)
                try:
                    request.session['current_dir']
                except KeyError:
                    request.session['current_dir'] = user.profile.home_dir.id
                    
                return HttpResponseRedirect('/')
            else:
                return HttpResponse("Your account is disabled.")
        else:
            messages.warning(request, 'Invalid login details supplied.')
            return render(request, 'users/login.html')
    else:
        return render(request, 'users/login.html')

@transaction.atomic
def register(request):
    context = RequestContext(request)

    registered = False

    if request.method == 'POST':
        user_form = UserForm(data=request.POST)

        if user_form.is_valid():
            data = user_form.cleaned_data
            f_password = data['password']
            f_username = data['username']
            f_name = data['first_name']
            f_last_name = data['last_name']
            if f_password == f_username or f_password == f_name or f_password == f_last_name:
                messages.warning(request, 'Password cannot be the same as username, name or last name.')
                return render(request,
            'users/register.html',
            {'user_form': user_form, 'registered': registered})
            user_profile = Profile()
            user = user_form.save()
            user.set_password(user.password)
            #user.birthday=cleaned_data["birthday"]

            home_dir = Directory()
            home_dir.created_t = timezone.now()
            home_dir.full_path = '/'

        #    try:
            #    with transaction.atomic():
            user.save()
            home_dir.owner = user
            home_dir.save()

            user_profile.user = user
            user_profile.home_dir = home_dir
            user_profile.save()
        #    except:
        #        return HttpResponse("BLAD PRZY ZAPISYWANIU DO BAZY")

            registered = True
            return HttpResponseRedirect('/users/login/')
        else:
            print(user_form.errors)

    else:
        user_form = UserForm()

    return render(request,
            'users/register.html',
            {'user_form': user_form, 'registered': registered})

def user_facebook(request):
    try:
        profile = Profile.objects.filter(user=request.user)[0]
    except IndexError:
        user_profile = Profile()
        home_dir = Directory()
        home_dir.created_t = timezone.now()
        home_dir.full_path = '/'
        home_dir.owner = request.user
        home_dir.save()
        user_profile.user = request.user
        user_profile.home_dir = home_dir
        user_profile.save()
    return HttpResponseRedirect('/') 
@login_required
def profile(request):
    default_pic =False
    try:
        file_storage = FileStorage.objects.filter(orig_owner=request.user,is_pic=True).order_by('-upload_t')[0]
    except IndexError:
        default_pic = True
    return render(request, 'users/profile.html',locals())


@sensitive_post_parameters()
@csrf_protect
@login_required
def user_password_change(request,
                    template_name='users/change.html',
                    post_change_redirect='/',
                    password_change_form=PasswordChangeForm,
                    current_app='users'):

    if request.method == "POST":
        form = password_change_form(user=request.user, data=request.POST)
        if form.is_valid():
            data = form.cleaned_data
            f_password = data['new_password1']
            if f_password == request.user.username or f_password == request.user.first_name or f_password == request.user.last_name:
                messages.warning(request, 'Password cannot be the same as username, name or last name.')
                context = {
                    'form': form,
                    'title': _('Password change'),
                }
                return TemplateResponse(request, template_name, context)
            if len(f_password) < 8:
                messages.warning(request, 'Password requires at least 8 characters.')
                context = {
                    'form': form,
                    'title': _('Password change'),
                }
                return TemplateResponse(request, template_name, context)     
            form.save()
            update_session_auth_hash(request, form.user)
            return HttpResponseRedirect('/')
    else:
        form = password_change_form(user=request.user)
    context = {
        'form': form,
        'title': _('Password change'),
    }

    if current_app is not None:
        request.current_app = current_app

    return TemplateResponse(request, template_name, context)

def user_password_reset(request):
    return password_reset(request,template_name='users/password_reset_form.html',
        email_template_name='users/password_reset_email.html',
        subject_template_name='users/password_reset_subject.txt',
        post_reset_redirect='reset-done/')

def user_password_reset_done(request):
    return password_reset_done(request,template_name='users/reset-done.html')

def user_password_reset_confirm(request,uidb64=None,token=None):
    return password_reset_confirm(request,template_name='users/password_reset_confirm.html',uidb64=uidb64,token=token,post_reset_redirect='complete/')

def user_password_reset_complete(request,uidb64=None,token=None):
    return render(request, 'users/complete.html')
@login_required
def edit_names(request, template_name="users/edit_names.html"):
    if request.method == "POST":
        form = ProfileAlterForm(data=request.POST,instance=request.user)
        if form.is_valid():
            user = form.save(commit=True)
            user.save()
            return HttpResponseRedirect('/users')
    else:
        if_facebook(request)
        facebook = request.session['if_f']
   
        form = ProfileAlterForm(instance=request.user)
    page_title = _('Edit user names')
    return render_to_response(template_name, locals(),
        context_instance=RequestContext(request))

@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect('/')

def if_facebook(request):
    try:
        UserSocialAuth.objects.get(user_id=request.user.id)
    except UserSocialAuth.DoesNotExist:
        request.session['if_f']="f"
    else:
        request.session['if_f']="t"

