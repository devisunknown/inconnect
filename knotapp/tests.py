from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core import mail
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from knotapp.models import Profile

User = get_user_model()


class EmailVerificationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='verifier', email='verify@example.com', password='pass12345'
        )
        self.profile, _ = Profile.objects.get_or_create(user=self.user)

    def tearDown(self):
        self.user.delete()

    def build_link(self):
        token = default_token_generator.make_token(self.user)
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        return reverse('verify_email', args=[uid, token])

    def test_signup_collects_email_and_sends_email(self):
        self.client.post(reverse('signup'), {
            'first_name': 'Jane', 'username': 'janedoe', 'email': 'jane@example.com',
            'password1': 'strongpass123', 'password2': 'strongpass123',
        })
        created = User.objects.get(username='janedoe')
        self.assertEqual(created.email, 'jane@example.com')
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('verify-email', mail.outbox[0].body)

    def test_verify_email_sets_flag(self):
        self.assertFalse(self.profile.email_verified)
        resp = self.client.get(self.build_link())
        self.assertEqual(resp.status_code, 200)
        self.profile.refresh_from_db()
        self.assertTrue(self.profile.email_verified)
        self.assertContains(resp, 'Email Verified')

    def test_verify_email_rejects_bad_token(self):
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        resp = self.client.get(reverse('verify_email', args=[uid, 'badtoken']))
        self.assertEqual(resp.status_code, 200)
        self.profile.refresh_from_db()
        self.assertFalse(self.profile.email_verified)
        self.assertContains(resp, 'Link Expired')

    def test_resend_requires_login(self):
        resp = self.client.post(reverse('resend_verification'), {})
        self.assertEqual(resp.status_code, 302)
        self.assertIn(reverse('login'), resp.get('Location'))
        self.assertIn('resend-verification', resp.get('Location'))

    def test_banner_shows_only_for_unverified(self):
        client = Client()
        client.force_login(self.user)
        resp = client.get(reverse('matches'))
        self.assertContains(resp, 'Verify your email to fully secure')

        self.profile.email_verified = True
        self.profile.save()
        resp = client.get(reverse('matches'))
        self.assertNotContains(resp, 'Verify your email to fully secure')


class LoginSignupRateLimitTests(TestCase):
    def setUp(self):
        cache.clear()
        self.user = User.objects.create_user(
            username='rluser', email='rl@example.com', password='pass12345'
        )

    def tearDown(self):
        cache.clear()
        self.user.delete()

    def test_login_blocks_after_rate_limit(self):
        cache.clear()
        url = reverse('login')
        for _ in range(15):
            self.client.post(url, {'username': 'rluser', 'password': 'wrongpass'})
        resp = self.client.post(url, {'username': 'rluser', 'password': 'pass12345'})
        self.assertContains(resp, 'Too many login attempts')
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_signup_blocks_after_rate_limit(self):
        cache.clear()
        url = reverse('signup')
        # Fresh anonymous client each attempt (after signup the client logs in
        # and would redirect; a fresh client stays anonymous). The IP-keyed
        # limit still accumulates across clients at 127.0.0.1. 20 attempts far
        # exceeds the 10/min cap and stays inside the single rate window.
        for i in range(20):
            client = Client()
            client.post(url, {
                'username': f'newuser{i}', 'email': f'u{i}@example.com',
                'password1': 'pass12345', 'password2': 'pass12345',
            })
        resp = self.client.post(url, {
            'username': 'finaluser', 'email': 'final@example.com',
            'password1': 'pass12345', 'password2': 'pass12345',
        })
        self.assertContains(resp, 'Too many signup attempts')
        self.assertFalse(User.objects.filter(username='finaluser').exists())


class PasswordResetTests(TestCase):
    def setUp(self):
        cache.clear()
        self.user = User.objects.create_user(
            username='resetter', email='reset@example.com', password='oldpass123'
        )

    def tearDown(self):
        cache.clear()
        self.user.delete()

    def build_confirm_url(self):
        token = default_token_generator.make_token(self.user)
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        return reverse('password_reset_confirm', args=[uid, token])

    def test_password_reset_sends_email(self):
        resp = self.client.post(reverse('password_reset'), {'email': 'reset@example.com'})
        self.assertRedirects(resp, reverse('password_reset_done'))
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('/reset/', mail.outbox[0].alternatives[0][0])

    def test_password_reset_full_flow(self):
        self.client.post(reverse('password_reset'), {'email': 'reset@example.com'})
        confirm_url = self.build_confirm_url()
        resp = self.client.get(confirm_url)
        self.assertContains(resp, 'Set New Password')

        resp = self.client.post(confirm_url, {
            'new_password1': 'brandnew123', 'new_password2': 'brandnew123',
        })
        self.assertRedirects(resp, reverse('password_reset_complete'))

        self.user.refresh_from_db()
        auth = authenticate(username='resetter', password='brandnew123')
        self.assertIsNotNone(auth)
        self.assertIsNone(authenticate(username='resetter', password='oldpass123'))

    def test_password_reset_rejects_invalid_token(self):
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        resp = self.client.get(reverse('password_reset_confirm', args=[uid, 'badtoken']))
        self.assertContains(resp, 'Link Invalid')

    def test_password_reset_rate_limited(self):
        cache.clear()
        url = reverse('password_reset')
        # 3/h cap - send more than 3 to guarantee the cap regardless of window.
        for _ in range(5):
            self.client.post(url, {'email': 'doesnot@exist.com'})
        resp = self.client.post(url, {'email': 'reset@example.com'})
        self.assertContains(resp, 'Too many reset attempts')
        self.assertEqual(len(mail.outbox), 0)
