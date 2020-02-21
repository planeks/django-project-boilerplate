from django.test import TestCase
from django.conf import settings


class SocialContextProcessorTests(TestCase):
    def setUp(self):
        from ..context_processors import social
        request = None
        self.context = social(request)

    def test_social(self):
        self.assertDictEqual(
            self.context,
            {
                'FACEBOOK_APP_ID': settings.FACEBOOK_APP_ID,
                'FACEBOOK_APP_SECRET': settings.FACEBOOK_APP_SECRET,
                'FACEBOOK_API_VERSION': settings.FACEBOOK_API_VERSION,
                'GOOGLE_CLIENT_ID': settings.GOOGLE_CLIENT_ID,
                'GOOGLE_CLIENT_SECRET': settings.GOOGLE_CLIENT_SECRET,
            })
