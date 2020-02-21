from django.test import TestCase
from ..models import User, FacebookProfile, GoogleProfile
from ..backends import FacebookBackend, GoogleBackend


class FacebookBackendTests(TestCase):
    def setUp(self):
        self.u1 = User.objects.create_user(
            'demo@mail.com', 'John Doe', 'demo')

        self.fp = FacebookProfile.objects.create(
            user=self.u1,
            access_token='test_token',
            userid='984851601558000',
        )

        self.backend = FacebookBackend()

    def test_facebook_backend(self):
        with self.settings(FACEBOOK_APP_SECRET='test'):
            user = self.backend.authenticate(
                email='demo@mail.com',
                facebook_secret='test',
            )
            user2 = self.backend.authenticate(
                email='unknown@mail.com',
                facebook_secret='test',
            )
            user3 = self.backend.authenticate()

            self.assertEqual(user, self.u1)
            self.assertEqual(user2, None)
            self.assertEqual(user3, None)
            self.assertEqual(
                self.backend.get_user(self.u1.id),
                self.u1)
            self.assertEqual(self.backend.get_user(222), None)


class GoogleBackendTests(TestCase):
    def setUp(self):
        self.u1 = User.objects.create_user(
            'demo@mail.com', 'John Doe', 'demo')

        self.fp = GoogleProfile.objects.create(
            user=self.u1,
            userid='984851601558000',
        )

        self.backend = GoogleBackend()

    def test_facebook_backend(self):
        with self.settings(GOOGLE_CLIENT_SECRET='ggtest'):
            user = self.backend.authenticate(
                email='demo@mail.com',
                google_secret='ggtest',
            )
            user2 = self.backend.authenticate(
                email='unknown@mail.com',
                google_secret='ggtest',
            )
            user3 = self.backend.authenticate()

            self.assertEqual(user, self.u1)
            self.assertEqual(user2, None)
            self.assertEqual(user3, None)
            self.assertEqual(
                self.backend.get_user(self.u1.id),
                self.u1)
            self.assertEqual(self.backend.get_user(222), None)
