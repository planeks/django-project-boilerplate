from unittest.mock import patch, call
from django.urls import reverse
from django.test import TestCase
from django.conf import settings
from collections import namedtuple
from oauth2client import client
from ..facebook import GraphAPI
from ..models import User


class BaseViewTests(TestCase):
    def setUp(self):
        self.u1 = User.objects.create_user(
            'demo@mail.com', 'John Doe', 'demo')


class ProfileViewTests(BaseViewTests):
    def setUp(self):
        super(ProfileViewTests, self).setUp()

    def test_unauthorized_access(self):
        """ Go to login page if unuauthorized user tries to open profile."""
        response = self.client.get(reverse('personal_information'), follow=True)
        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            [(a.replace('%2F', '/'), b) for a, b in response.redirect_chain],
            [
                (
                    reverse('login') + '?next=' + reverse('personal_information'),
                    302,
                ),
            ],
        )

    def test_authorized_access(self):
        """ Check profile page for authorized user."""
        self.client.force_login(self.u1)
        response = self.client.get(reverse('personal_information'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['user'], self.u1)


class LoginViewTest(BaseViewTests):
    def setUp(self):
        super(LoginViewTest, self).setUp()

    def test_login_page_authorized(self):
        """ Redirect to profile if user is already logged in."""
        self.client.force_login(self.u1)
        response = self.client.get(reverse('login'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.redirect_chain,
            [(reverse('personal_information'), 302)],
        )

    def test_login_page_redirection_loop(self):
        """ Raise exception if user tries to go to the /login/?next=/login/ page."""
        self.client.force_login(self.u1)
        with self.assertRaises(ValueError):
            self.client.get(reverse('login')+'?next=/login/', follow=True)

    def test_form_validation(self):
        response = self.client.post(
            reverse('login'),
            data={
                'username': 'demo@mail.com',
                'password': 'demo',
            },
            follow=True)
        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            response.redirect_chain,
            [(reverse('personal_information'), 302)],
        )

        self.assertTrue(response.context['user'].is_active)
        self.assertEqual(response.context['user'], self.u1)


class RegisterViewTests(BaseViewTests):
    def setUp(self):
        super(RegisterViewTests, self).setUp()

    def test_as_authorized(self):
        self.client.force_login(self.u1)
        response = self.client.get(reverse('register'), follow=True)
        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            response.redirect_chain,
            [(reverse('personal_information'), 302)],
        )

    def test_form_render(self):
        from ..forms import UserRegistrationForm
        response = self.client.get(reverse('register'))
        self.assertIsInstance(
            response.context['form'], UserRegistrationForm)

    def test_form_validation(self):
        # from django.core import mail
        response = self.client.post(
            reverse('register'),
            data={
                'email': 'blah@mail.com',
                'name': 'Emilia Clarke',
                'password1': '123456',
                'password2': '123456',
            },
            follow=True)
        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            response.redirect_chain,
            [(reverse('personal_information'), 302)],
        )

        u = User.objects.get(email='blah@mail.com')
        self.assertEqual(u.name, 'Emilia Clarke')


def _fake_get_user_from_cookie(*args):
    return {
        'access_token': 'yummy',
    }


class FacebookLoginTests(TestCase):
    def setUp(self):
        self.u1 = User.objects.create_user(
            'demo@mail.com', 'John Doe', 'demo')

    @patch(
        'apps.accounts.facebook.get_user_from_cookie',
        _fake_get_user_from_cookie)
    @patch.object(GraphAPI, 'get_object', autospec=True)
    def test_login_for_existing_user(
            self,
            mock_get_object):
        mock_get_object.return_value = {
            'access_token': 'yummi',
            'email': 'demo@mail.com',
            'name': 'John Doe',
            'gender': 'male',
            'id': '984851601558000',
            'link':
            'https://www.facebook.com/app_scoped_user_id/984851601558000/',
            'timezone': 3,
            'locale': 'en_US',
        }
        response = self.client.get(reverse('fb_login'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('redirect_url', response.context)
        self.assertEqual(
            int(self.client.session['_auth_user_id']), self.u1.pk)

        user = User.objects.get(pk=self.u1.pk)
        fbp = user.facebook_profile
        self.assertEqual(fbp.userid, '984851601558000')

    @patch(
        'apps.accounts.facebook.get_user_from_cookie',
        _fake_get_user_from_cookie)
    @patch.object(GraphAPI, 'get_object', autospec=True)
    def test_login_for_new_user(
            self,
            mock_get_object):
        mock_get_object.return_value = {
            'access_token': 'yummi',
            'email': 'demo2@mail.com',
            'name': 'Leslie Judd',
            'gender': 'female',
            'id': '984851601558000',
            'link':
            'https://www.facebook.com/app_scoped_user_id/984851601558000/',
            'timezone': 3,
            'locale': 'en_US',

        }
        response = self.client.get(reverse('fb_login'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('redirect_url', response.context)

        user = User.objects.get(pk=int(self.client.session['_auth_user_id']))
        self.assertEqual(user.name, 'Leslie Judd')
        self.assertEqual(user.email, 'demo2@mail.com')

        fbp = user.facebook_profile
        self.assertEqual(fbp.userid, '984851601558000')

    @patch(
        'apps.accounts.facebook.get_user_from_cookie',
        _fake_get_user_from_cookie)
    @patch.object(GraphAPI, 'get_object', autospec=True)
    def test_already_logged_in_user(
            self,
            mock_get_object):
        mock_get_object.return_value = {
            'access_token': 'yummi',
            'email': 'demo@mail.com',
            'name': 'John Doe',
            'gender': 'male',
            'id': '984851601558000',
            'link':
            'https://www.facebook.com/app_scoped_user_id/984851601558000/',
            'timezone': 3,
            'locale': 'en_US',

        }
        self.client.force_login(self.u1)
        response = self.client.get(reverse('fb_login'))
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('redirect_url', response.context)
        self.assertIn('Ви вже залогінені'.encode('utf8'), response.content)


class GoogleLoginTests(TestCase):
    def setUp(self):
        self.u1 = User.objects.create_user(
            'demo@mail.com', 'John Doe', 'demo')

    @patch.object(client, 'credentials_from_code', autospec=True)
    def test_login_for_existing_user(
            self,
            mock_credentials_from_code):
        Credentials = namedtuple('Credentials', 'id_token')
        mock_credentials_from_code.return_value = Credentials(
            id_token={
                'sub': '111111',
                'email': 'demo@mail.com',
                'name': 'John Doe',
            },
        )
        response = self.client.post(
            reverse('gg_login'), data={'data': 'demo'})
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            str(response.content, encoding='utf8'),
            {'redirect_url': settings.LOGIN_REDIRECT_URL},
        )
        self.assertEqual(
            int(self.client.session['_auth_user_id']), self.u1.pk)

        user = User.objects.get(pk=self.u1.pk)
        ggp = user.google_profile
        self.assertEqual(ggp.userid, '111111')

    @patch.object(client, 'credentials_from_code', autospec=True)
    def test_login_for_new_user(
            self,
            mock_credentials_from_code):
        Credentials = namedtuple('Credentials', 'id_token')
        mock_credentials_from_code.return_value = Credentials(
            id_token={
                'sub': '111111',
                'email': 'demo2@mail.com',
                'name': 'Leslie Judd',
            },
        )
        response = self.client.post(
            reverse('gg_login'), data={'data': 'demo'})
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            str(response.content, encoding='utf8'),
            {'redirect_url': reverse('personal_information')},
        )

        user = User.objects.get(pk=int(self.client.session['_auth_user_id']))
        self.assertEqual(user.name, 'Leslie Judd')
        self.assertEqual(user.email, 'demo2@mail.com')

        ggp = user.google_profile
        self.assertEqual(ggp.userid, '111111')

    @patch.object(client, 'credentials_from_code', autospec=True)
    def test_already_logged_in_user(
            self,
            mock_credentials_from_code):
        Credentials = namedtuple('Credentials', 'id_token')
        mock_credentials_from_code.return_value = Credentials(
            id_token={
                'sub': '111111',
                'email': 'demo@mail.com',
                'name': 'John Doe',
            },
        )
        self.client.force_login(self.u1)
        response = self.client.post(
            reverse('gg_login'), data={'data': 'demo'})
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            str(response.content, encoding='utf8'),
            {},
        )
