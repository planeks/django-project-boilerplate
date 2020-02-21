from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    User,
    FacebookProfile,
    GoogleProfile,
    UserInvite,
    UserGroup,
)
from .forms import UserChangeForm, UserCreationForm


class FacebookProfileInline(admin.StackedInline):
    model = FacebookProfile


class GoogleProfileInline(admin.StackedInline):
    model = GoogleProfile


class UserAdmin(BaseUserAdmin):
    # add_form_template = 'accounts/admin/auth/user/add_form.html'
    fieldsets = (
        (None, {
            'fields': (
                'email', 'name', 'role', 'phone',
                'language',
                'time_zone',
                'avatar', 'avatar_text', 'avatar_color',
                'data',
                'is_internal', 'is_administrator', 'user_groups',
                'one_time_link_support',
                'permanent_activation_link',
                'permanent_activation_token',
                'hidden_section_keys', 'hidden_site_keys',
                'is_readonly',
                'password',
            )}),
        (_('Permissions'), {
            'fields': (
                'is_active', 'is_staff',
                'is_superuser',
                'groups',
                'user_permissions',
            )}),
        (_('Important dates'), {
            'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email', 'name', 'role', 'phone',
                'language',
                'time_zone',
                'password1', 'password2')
        }),
    )

    list_display = (
        'email', 'name', 'role', 'phone',
        'language',
        'time_zone',
        'avatar_text', 'avatar_color_preview',
        'is_internal', 'is_administrator',
        'is_staff', 'is_superuser', 'is_active',
        'date_joined', 'last_login', 'has_usable_password', 'account_activation_url', 'is_readonly',
    )
    list_filter = (
        'is_internal', 'is_administrator',
        'is_staff', 'is_superuser',
        'is_active', 'groups',
    )
    search_fields = ('email', 'name', 'phone', 'role')
    ordering = ('email', '-date_joined')
    date_hierarchy = 'date_joined'
    filter_horizontal = ('groups', 'user_permissions', 'user_groups')
    inlines = [FacebookProfileInline, GoogleProfileInline]

    form = UserChangeForm
    add_form = UserCreationForm
    actions = [
        'activate',
        'deactivate',
        'set_unusable_password',
    ]

    def get_urls(self):
        from django.conf.urls import url
        return [
            url(
                r'^(.+)/change/password/$',
                self.admin_site.admin_view(self.user_change_password),
                name='auth_user_password_change',
            ),
        ] + super().get_urls()

    def activate(self, request, queryset):
        queryset.update(is_active=True)
    activate.short_description = \
        _('Activate')

    def deactivate(self, request, queryset):
        queryset.update(is_active=False)
    deactivate.short_description = \
        _('Deactivate')

    def set_unusable_password(self, request, queryset):
        for q in queryset:
            q.set_unusable_password()
            q.save()
    set_unusable_password.short_description = \
        _('Set unusable password')

    def avatar_color_preview(self, obj):
        from django.utils.html import mark_safe
        return mark_safe(
            '<span style="background:{color};padding:2px 4px;color:white;'
            'border-radius:2px;font-family:monospace;">{color}</span>'.format(color=obj.avatar_color))

    def account_activation_url(self, obj):
        from django.utils.html import mark_safe
        if obj.one_time_link_support:
            url = obj.get_account_activation_url()
            if url:
                return mark_safe('<a href="%s" target="_blank">Activation link</a>' % url)
        else:
            return 'Not supported'
    account_activation_url.short_description = \
        _('Activation URL')

admin.site.register(User, UserAdmin)


@admin.register(UserInvite)
class UserInviteAdmin(admin.ModelAdmin):
    list_display = (
        'email', 'sent_by', 'added', 'is_internal', 'is_administrator',
        'registered_user', 'registration_date')
    date_hierarchy = 'added'
    search_fields = ('email',)
    list_filter = ('is_internal',)
    raw_id_fields = ('sent_by', 'registered_user')
    actions = [
        'send_to_email',
    ]

    def send_to_email(self, request, queryset):
        for q in queryset:
            q.send_to_email()

    send_to_email.short_description = _('Send to email')


@admin.register(UserGroup)
class UserGroupAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
