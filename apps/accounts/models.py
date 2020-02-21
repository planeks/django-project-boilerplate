from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.utils import timezone
from django.db.models.signals import pre_save, post_delete
from django.contrib.postgres.fields import JSONField, ArrayField
from django.dispatch import receiver
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
import uuid
import pytz
import random
import string


class UserManager(BaseUserManager):
    """
    Creates and saves a User with the given email, phone, password and optional extra info.
    """
    def _create_user(self, email,
                     name,
                     password,
                     is_staff, is_superuser, **extra_fields):
        """
        Creates and saves a User with the given username, email and password.
        """
        now = timezone.now()

        if not email:
            raise ValueError('The given email must be set')

        email = self.normalize_email(email)
        user = self.model(
            email=email,
            name=name or '',
            is_staff=is_staff, is_active=True,
            is_superuser=is_superuser,
            date_joined=now,
            last_login=now,
            **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, name, password=None, **extra_fields):
        return self._create_user(email, name, password, False, False, **extra_fields)

    def create_superuser(
            self, email, name, password=None, **extra_fields):
        """
        Creates and saves a superuser with the given email,
        phone and password.
        """
        return self._create_user(email, name, password, True, True, **extra_fields)

    def get_by_natural_key(self, email):
        return self.get(email__iexact=email)


def generate_avatar_filename(instance, filename):
    ext = filename.split('.')[-1]
    url = 'images/avatars/%s.%s' % (
        instance.id,
        ext)
    return url


class User(AbstractBaseUser, PermissionsMixin):
    """
    A model which implements the authentication model.

    Email and password are required. Other fields are optional.

    Email field are used for logging in.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(_('Email'), max_length=255, unique=True)
    name = models.CharField(_('Full name'), max_length=255)

    role = models.CharField(_('Role'), max_length=255, blank=True, default='')
    phone = models.CharField(_('Phone'), max_length=255, blank=True, default='')

    data = JSONField(_('Data'), default=dict, blank=True)

    language = models.CharField(_('Language'), default='en', max_length=10, choices=settings.LANGUAGES)
    time_zone = models.CharField(
        _('Timezone'), default='UTC', max_length=60, choices=((x, x) for x in pytz.all_timezones))
    avatar = models.ImageField(
        _('Avatar'),
        null=True, blank=True,
        upload_to=generate_avatar_filename,
        help_text=_(
            'Optional avatar. We recommend to use PNG '
            ' or JPG with size 50x50 pixels.'),
    )
    avatar_text = models.CharField(_('Avatar text'), max_length=2, default='XX')
    avatar_color = models.CharField(_('Avatar color (HEX)'), max_length=25, default='#cccccc')

    is_internal = models.BooleanField(_('Internal user'), default=False)
    is_administrator = models.BooleanField(_('Administrator'), default=False)
    one_time_link_support = models.BooleanField(_('One time link support'), default=False)
    permanent_activation_link = models.BooleanField(_('Permanent activation link'), default=False)
    permanent_activation_token = models.CharField(
        _('Permanent activation token'), default='', blank=True, max_length=100)
    hidden_section_keys = ArrayField(
        models.CharField(max_length=70),
        verbose_name=_('Hidden section keys'), default=list, blank=True,
        help_text=_(
            'Comma separated list of section keys '
            'you want to exclude from the side menu.'),
    )
    hidden_site_keys = ArrayField(
        models.CharField(max_length=70),
        verbose_name=_('Hidden site keys'), default=list, blank=True,
        help_text=_(
            'Comma separated list of site keys '
            'you want to exclude from the side menu.'),
    )

    is_readonly = models.BooleanField(_('Read only'), default=False)
    user_groups = models.ManyToManyField(
        'UserGroup', related_name='users', blank=True,
    )

    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )

    date_joined = models.DateTimeField(_('Date joined'), default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        ordering = ['name', '-date_joined']

    def get_first_name(self):
        chunks = self.name.split()
        if len(chunks) >= 1:
            return chunks[0]
        else:
            return ''

    @property
    def first_name(self):
        return self.get_first_name()

    def get_last_name(self):
        chunks = self.name.split()
        if len(chunks) >= 2:
            return chunks[1]
        else:
            return ''

    @property
    def last_name(self):
        return self.get_last_name()

    def __str__(self):
        return self.name

    @staticmethod
    def get_avatar_text(name: str) -> str:
        """ Generates a text for automatically generated avatar from first letters
        of the first name and last name."""
        chunks = name.split()
        if len(chunks) >= 2:
            return chunks[0][0].upper() + chunks[1][0].upper()
        elif len(chunks) == 1:
            return chunks[0][:2].upper()
        else:
            return 'XX'

    @staticmethod
    def get_avatar_color(id: int) -> str:
        """ Generates a color of the avatar background based on the user id."""
        from apps.core.utils import Color, generate_random_color, color_to_hex
        white = Color(120, 120, 120)
        my_color = generate_random_color(mix=white, id=id)
        return color_to_hex(my_color)

    def get_uidb64(self):
        from django.utils.http import urlsafe_base64_encode
        return urlsafe_base64_encode(str(self.pk).encode('utf8'))

    def get_activation_token(self):
        from .tokens import account_activation_token
        return account_activation_token.make_token(self)

    def get_account_activation_url(self):
        from django.urls import reverse
        if self.permanent_activation_link:
            if self.permanent_activation_token:
                return reverse('manage:activate_account', args=[
                    self.get_uidb64(),
                    self.permanent_activation_token,
                ])
        else:
            return reverse('manage:activate_account', args=[
                self.get_uidb64(),
                self.get_activation_token(),
            ])

    def get_email_md5_hash(self):
        import hashlib
        m = hashlib.md5(self.email.lower().encode('utf-8')).hexdigest()
        return m

    def has_usable_password(self) -> bool:
        return super().has_usable_password()
    has_usable_password.boolean = True

    @property
    def days_on_site(self):
        from django.utils.timezone import now
        delta = now() - self.date_joined
        return delta.days

    @property
    def has_api_token(self):
        from rest_framework.authtoken.models import Token
        return Token.objects.filter(user=self).exists()

    def get_api_token(self):
        from rest_framework.authtoken.models import Token
        try:
            t = Token.objects.get(user=self)
            return t.key
        except Token.DoesNotExist:
            pass

    def get_reverse_relations(self):
        from apps.data.models import RecordProperty, Record
        relations = RecordProperty.objects.filter(
            type__in=[
                RecordProperty.USER_RELATION_UNIQUE,
                RecordProperty.USER_RELATION,
                RecordProperty.MULTIPLE_USERS_RELATION])
        for rel in relations:
            rel.records_count = rel.get_reverse_related_records_count(
                self,
                attr_name='email',
            )
        return relations

    def get_json(self, include_related=None):
        return self.get_dict(jsonize=True, include_related=include_related)

    def get_dict(self, jsonize=False, include_related=None):
        import datetime
        DATETIME_FORMAT = '%Y-%m-%d'

        _data = None
        if not _data:
            _data = {
                'id': self.id, 'name': self.name, 'email': self.email, 'phone': self.phone, 'role': self.role,
                'date_joined': self.date_joined.strftime(DATETIME_FORMAT) if jsonize else self.date_joined,
                'avatar': self.avatar.url if self.avatar else None,
                'avatar_color': self.avatar_color, 'avatar_text': self.avatar_text,
                'days_on_site': self.days_on_site, 'data': self.data, 'is_internal': self.is_internal,
                'is_readonly': self.is_readonly, 'is_administrator': self.is_administrator,
                'language': self.language, 'time_zone': self.time_zone,
                'groups': [
                    {
                        'id': x.id,
                        'name': x.name,
                    } for x in self.user_groups.all()
                ]}
        return _data

    def execute_scenario(self, trigger, use_celery=True):
        # For debug purposes, use Celery task directly in management views
        from apps.automation.tasks import execute_triggered_scenarios_for_user
        if use_celery:
            execute_triggered_scenarios_for_user.delay(None, self.id, trigger)
        else:
            execute_triggered_scenarios_for_user(None, self.id, trigger)

    def get_related_records(self):
        # TODO: try to delete after some time
        from apps.data.models import RecordProperty, Record
        result = {}
        relations = RecordProperty.objects.filter(
            type__in=[
                RecordProperty.USER_RELATION_UNIQUE,
                RecordProperty.USER_RELATION,
                RecordProperty.MULTIPLE_USERS_RELATION])
        # print(relations)
        if relations:
            from elasticsearch import Elasticsearch
            es = Elasticsearch(settings.ELASTICSEARCH_URLS)
            for rel in relations:
                collection = rel.record_type.collection
                # print(collection)
                index_name = collection.get_es_index_name()
                # print(index_name)
                if es.indices.exists(index=index_name):
                    _body = {
                        'query': {
                            'multi_match': {
                                'query': str(self.email),
                                'fields': 'prop_%s' % rel.key,
                            }
                        }
                    }
                    res = es.search(
                        index=index_name,
                        body=_body,
                    )
                    if 'hits' in res:
                        ids = [x['_id'] for x in res['hits']['hits']]
                        _records = Record.objects.filter(id__in=ids)
                        _records = {str(x.id): x for x in _records}
                        records = [_records[id] for id in ids if id in _records.keys()]
                        total = res['hits']['total']
                        if type(total) is not int:
                            total = total['value']

                        result[collection.key] = {
                            'collection': collection,
                            'total': total,
                            'records': records,
                        }
        return result

    def save(self, *args, **kwargs):
        """ Fill a part of data automatically.
        """
        # self.email = self.email.lower()
        if self.avatar_text == 'XX' or not self.avatar_text:
            self.avatar_text = self.get_avatar_text(self.name)
        if self.avatar_color == '#cccccc' or not self.avatar_color:
            self.avatar_color = self.get_avatar_color(self.pk)
        if not self.permanent_activation_token:
            from django.utils.crypto import get_random_string
            self.permanent_activation_token = '%s-%s' % (
                get_random_string(13, "abcdefghijklmnopqrstuvwxyz0123456789"),
                get_random_string(20, "abcdefghijklmnopqrstuvwxyz0123456789"),
            )
        super().save(*args, **kwargs)


@receiver(pre_save, sender=User)
def product_image_pre_save_listener(sender, instance: User, **kwargs):
    if instance.pk:
        try:
            p_u = User.objects.get(pk=instance.pk)
            if p_u.avatar and p_u.avatar != instance.avatar:
                p_u.avatar.delete(save=False)

            if p_u.email != instance.email:
                # Email has been changed, so we should check all user relations in the database
                related_records = p_u.get_related_records()
                for c_key, chunk in related_records.items():
                    records = chunk['records']
                    if records:
                        from apps.data.tasks import change_related_user_email
                        for record in records:
                            change_related_user_email.delay(record.id, p_u.email, instance.email)
        except User.DoesNotExist:
            pass


@receiver(post_delete, sender=User)
def user_avatar_post_delete_listener(sender, instance: User, **kwargs):
    if instance.avatar:
        instance.avatar.delete(save=False)


class FacebookProfile(models.Model):
    user = models.OneToOneField(
        User,
        related_name='facebook_profile',
        verbose_name=_('User'), on_delete=models.CASCADE)
    access_token = models.TextField(_('Access token'))
    userid = models.CharField(_('User ID'), max_length=100)

    class Meta:
        verbose_name = _('Facebook profile')
        verbose_name_plural = _('Facebook profiles')


class GoogleProfile(models.Model):
    user = models.OneToOneField(
        User,
        related_name='google_profile',
        verbose_name=_('User'), on_delete=models.CASCADE)
    userid = models.CharField(_('User ID'), max_length=100)

    class Meta:
        verbose_name = _('Google profile')
        verbose_name_plural = _('Google profiles')


class UserInvite(models.Model):
    code = models.CharField(_('Code'), max_length=100, blank=True)
    email = models.EmailField(_('Email'), max_length=255)
    user_groups = models.ManyToManyField(
        'UserGroup', related_name='user_invites', blank=True,
    )

    is_internal = models.BooleanField(_('Internal user'), default=False)
    is_administrator = models.BooleanField(_('Administrator'), default=False)

    sent_by = models.ForeignKey(
        User, related_name='invites_sent', verbose_name=_('Sent by'),
        null=True, blank=True,
        on_delete=models.CASCADE,
    )

    registered_user = models.OneToOneField(
        User, related_name='invite', verbose_name=_('Registered user'),
        blank=True, null=True,
        on_delete=models.CASCADE,
    )
    registration_date = models.DateTimeField(_('Registration date'), blank=True, null=True)

    added = models.DateTimeField(_('Added'), auto_now_add=True)

    CODE_LENGTH = 30

    class Meta:
        verbose_name = _('User invite')
        verbose_name_plural = _('User invites')

    def __str__(self):
        return self.email

    def get_registration_url(self):
        from django.urls import reverse
        return '%s%s?invite_code=%s' % (
            settings.SITE_URL,
            reverse('manage:register'),
            self.code,
        )

    def send_to_email(self):
        from apps.core.utils import send_mail
        send_mail(
            to=[self.email],
            subject=_('Invitation for registration on Tabbli'),
            html_template='accounts/email/invite.html',
            txt_template='accounts/email/invite.txt',
            context={'invite': self})

    def save(self, *args, **kwargs):
        """ Fill a code automatically.
        """
        if not self.code:
            letters = string.ascii_lowercase
            while True:
                _code = ''.join(random.choice(letters) for i in range(self.CODE_LENGTH))
                if not UserInvite.objects.filter(code=_code).exists():
                    self.code = _code
                    break
        super().save(*args, **kwargs)


class UserGroup(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_('Name'), unique=True, max_length=255)

    class Meta:
        verbose_name = _('User group')
        verbose_name_plural = _('User groups')
        ordering = ['name']

    def __str__(self):
        return self.name
