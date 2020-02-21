from django.urls import path, re_path
from django.contrib.auth import views as auth_views
from django.conf import settings
from . import views


urlpatterns = [
    path('login/', views.login_view, name='login'),
    # path('fb-login/', views.fb_login, name='fb_login'),
    # path('gg-login/', views.gg_login, name='gg_login'),

    # path(
    #     'logout/',
    #     auth_views.LogoutView.as_view(),
    #     {'template_name': 'accounts/logout.html'}, name='logout'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),
    path(
        'password-change/',
        auth_views.PasswordChangeView.as_view(),
        {
            'template_name': 'accounts/password_change_form.html',
            'post_change_redirect': 'password_change_done',
        },
        name='password-change'),
    path(
        'password-change/done/',
        auth_views.PasswordChangeDoneView.as_view(),
        {'template_name': 'accounts/password_change_done.html'},
        name='password-change-done'),
    path('password-reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    re_path(
        r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    re_path(
        r'^reset/done/$',
        auth_views.PasswordResetDoneView.as_view(), name='password_reset_complete'),
    # path('profile/personal-information/', views.personal_information, name='personal_information'),
    # path('profile/personal-information/edit/', views.edit_personal_information, name='edit_personal_information'),
]
