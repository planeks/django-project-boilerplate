from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.http import JsonResponse, HttpResponseForbidden, HttpResponse
from django.utils.translation import ugettext as _
# from django.utils.module_loading import import_string
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse, reverse_lazy
# from django.contrib.sites.shortcuts import get_current_site
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q
from .models import (
    User,
    FacebookProfile,
    GoogleProfile,
    UserInvite,
)
from .forms import EditUserForm
from apps.core.utils import turbolinks_redirect
import logging


logger = logging.getLogger(__name__)


RESET_LINK_EXPIRATION = 60


# @login_required
# def personal_information(request, template_name='accounts/personal_information.html'):
#     user = request.user
#     information_form = EditUserForm(instance=user)
#     context = {
#         'user': user,
#         'information_form': information_form,
#         'menu': 'personal_information',
#     }
#     return render(request, template_name, context)


# @login_required
# def edit_personal_information(request, template_name='accounts/edit_personal_information.html'):
#     user = request.user
#     if request.method == 'POST':
#         form = EditUserForm(instance=user, data=request.POST, files=request.FILES)
#         if form.is_valid():
#             form.save()
#             return redirect(reverse('personal_information'))
#     else:
#         form = EditUserForm(instance=user)
#     context = {
#         'form': form,
#         'menu': 'personal_information',
#     }
#     return render(request, template_name, context)

# @csrf_exempt
def login_view(request, template_name='accounts/login.html'):
    from .forms import UserAuthForm
    # from django.core.exceptions import ObjectDoesNotExist

    redirect_to = request.POST.get('next', request.GET.get('next', ''))
    do_redirect = False

    if request.user.is_authenticated:
        if redirect_to == request.path:
            raise ValueError('Redirection loop for authenticated user detected.')
        return redirect(reverse('manage:dashboard'))
    elif request.method == 'POST':
        if not request.META['HTTP_USER_AGENT'].endswith(settings.TABBLI_IOS_APP_USER_AGENT):
            template_name = 'accounts/includes/login_form.html'
        form = UserAuthForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            if request.META['HTTP_USER_AGENT'].endswith(settings.TABBLI_IOS_APP_USER_AGENT):
                return redirect(reverse('manage:collections_list'))

            if redirect_to == '':
                redirect_to = reverse('manage:dashboard')
            do_redirect = True
    else:
        form = UserAuthForm(request)

    context = {
        'form': form,
        'next': redirect_to,
        'do_redirect': do_redirect,
    }
    return render(request, template_name, context)


# def fb_login(request):
#     from .facebook import (
#         get_user_from_cookie,
#         GraphAPI,
#     )
#     from django.contrib.auth import authenticate, login
#
#     context = {
#         'user': request.user,
#     }
#
#     if request.user.is_anonymous:
#         cookie = get_user_from_cookie(
#             request.COOKIES,
#             settings.FACEBOOK_APP_ID,
#             settings.FACEBOOK_APP_SECRET)
#         if cookie:
#             graph = GraphAPI(cookie["access_token"])
#             profile = graph.get_object("me")
#             args = {'fields': 'id,name,email'}
#             profile = graph.get_object("me", **args)
#
#             email = profile.get('email')
#             name = profile.get('name', '')
#             access_token = cookie['access_token']
#
#             user = authenticate(
#                 email=email,
#                 facebook_secret=settings.FACEBOOK_APP_SECRET)
#             if user:
#                 # User with given email exists
#                 login(request, user)
#                 context.update({
#                     'redirect_url': settings.LOGIN_REDIRECT_URL,
#                 })
#             else:
#                 # Create new user
#                 new_user = User(
#                     email=email,
#                     name=name,
#                     last_login=timezone.now(),
#                 )
#                 new_user.save()
#                 new_user.set_unusable_password()
#                 user = authenticate(
#                     email=email,
#                     facebook_secret=settings.FACEBOOK_APP_SECRET)
#                 login(request, user)
#                 context.update({
#                     'redirect_url': reverse('personal_information'),
#                 })
#
#             # Fill the FB profile
#             try:
#                 fbp = FacebookProfile.objects.get(user=user)
#             except FacebookProfile.DoesNotExist:
#                 fbp = FacebookProfile(user=user)
#             fbp.access_token = access_token
#             fbp.userid = profile.get('id')
#             fbp.save()
#
#     return render(request, 'accounts/fb_login.html', context)


# @csrf_exempt
# @require_POST
# def gg_login(request):
#     from oauth2client import client
#     from django.contrib.auth import authenticate, login
#
#     auth_code = request.body
#     context = {}
#
#     if request.user.is_anonymous:
#         credentials = client.credentials_from_code(
#             client_id=settings.GOOGLE_CLIENT_ID,
#             client_secret=settings.GOOGLE_CLIENT_SECRET,
#             scope=['profile', 'email'],
#             code=auth_code,
#         )
#         userid = credentials.id_token['sub']
#         email = credentials.id_token['email']
#         name = credentials.id_token['name']
#
#         user = authenticate(
#             email=email,
#             google_secret=settings.GOOGLE_CLIENT_SECRET)
#
#         if user:
#             # User with given email exists
#             login(request, user)
#             context.update({
#                 'redirect_url': settings.LOGIN_REDIRECT_URL,
#             })
#         else:
#             # Create new user
#             new_user = User(
#                 email=email,
#                 name=name,
#                 last_login=timezone.now(),
#             )
#             new_user.save()
#             new_user.set_unusable_password()
#             user = authenticate(
#                 email=email,
#                 google_secret=settings.GOOGLE_CLIENT_SECRET)
#             login(request, user)
#             context.update({
#                 'redirect_url': reverse('personal_information'),
#             })
#
#         # Fill the FB profile
#         try:
#             ggp = GoogleProfile.objects.get(user=user)
#         except GoogleProfile.DoesNotExist:
#             ggp = GoogleProfile(user=user)
#         ggp.userid = userid
#         ggp.save()
#
#     return JsonResponse(context)


def register(request, template_name='accounts/register.html'):
    from .forms import UserRegistrationForm
    if request.user.is_authenticated:
        return redirect(reverse('personal_information'))

    invite_code = request.GET.get('invite_code', '')
    valid_invite = False
    do_redirect = False
    redirect_to = request.POST.get('next', request.GET.get('next', ''))

    if request.method == 'POST':
        template_name = 'accounts/includes/register_form.html'
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            invite_code = form.cleaned_data['invite_code']

            if invite_code:
                try:
                    invite = UserInvite.objects.get(code=invite_code, registered_user=None)
                    valid_invite = True

                    user = form.save(commit=False)
                    user.save()
                    user.backend = 'django.contrib.auth.backends.ModelBackend'

                    invite.registered_user = user
                    invite.registration_date = timezone.now()
                    invite.save()

                    user.is_internal = invite.is_internal
                    user.save()
                    login(request, user)
                except UserInvite.DoesNotExist:
                    return HttpResponseForbidden('Unknown invite code')

            do_redirect = True
            redirect_to = reverse('manage:my_profile')
    else:
        initial = {'invite_code': invite_code}
        try:
            invite = UserInvite.objects.get(code=invite_code, registered_user=None)
            initial['email'] = invite.email
            valid_invite = True
        except UserInvite.DoesNotExist:
            pass
        form = UserRegistrationForm(initial=initial)

    context = {
        'next': redirect_to,
        'do_redirect': do_redirect,
        'form': form,
        'invite_code': invite_code,
        'valid_invite': valid_invite,
    }
    return render(request, template_name, context)


def logout_view(request):
    _next = request.GET.get('next')
    logout(request)
    return redirect(_next if _next else settings.LOGOUT_REDIRECT_URL)
