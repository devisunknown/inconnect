from django.contrib.auth import authenticate, get_user_model
from django.core import mail
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


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
