import json
from django.test import TestCase, Client
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from knotapp.models import Interest, Profile


class APITestBase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.interest1 = Interest.objects.create(name='Music', icon='🎵', category='Arts')
        cls.interest2 = Interest.objects.create(name='Gaming', icon='🎮', category='Entertainment')
        cls.interest3 = Interest.objects.create(name='Fitness', icon='💪', category='Health')
        cls.interest4 = Interest.objects.create(name='Travel', icon='✈️', category='Lifestyle')


class SignupAPITest(APITestBase):
    def setUp(self):
        self.client = Client()
        self.url = '/api/auth/signup/'

    def test_successful_signup(self):
        resp = self.client.post(self.url, json.dumps({
            'first_name': 'Jane',
            'username': 'jane_test',
            'email': 'jane@test.com',
            'password1': 'SecurePass123!',
            'password2': 'SecurePass123!',
        }), content_type='application/json')
        self.assertEqual(resp.status_code, 201)
        self.assertIn('token', resp.data)
        self.assertEqual(resp.data['user']['username'], 'jane_test')
        self.assertTrue(Token.objects.filter(user__username='jane_test').exists())

    def test_signup_creates_profile(self):
        self.client.post(self.url, json.dumps({
            'first_name': 'Bob',
            'username': 'bob_test',
            'email': 'bob@test.com',
            'password1': 'SecurePass123!',
            'password2': 'SecurePass123!',
        }), content_type='application/json')
        self.assertTrue(Profile.objects.filter(user__username='bob_test').exists())

    def test_duplicate_username(self):
        User.objects.create_user('taken', password='pass1234!')
        resp = self.client.post(self.url, json.dumps({
            'first_name': 'X',
            'username': 'taken',
            'email': 'x@test.com',
            'password1': 'SecurePass123!',
            'password2': 'SecurePass123!',
        }), content_type='application/json')
        self.assertEqual(resp.status_code, 400)
        self.assertIn('username', resp.data)

    def test_duplicate_email(self):
        User.objects.create_user('other', email='dup@test.com', password='pass1234!')
        resp = self.client.post(self.url, json.dumps({
            'first_name': 'X',
            'username': 'new_user',
            'email': 'dup@test.com',
            'password1': 'SecurePass123!',
            'password2': 'SecurePass123!',
        }), content_type='application/json')
        self.assertEqual(resp.status_code, 400)
        self.assertIn('email', resp.data)

    def test_password_mismatch(self):
        resp = self.client.post(self.url, json.dumps({
            'first_name': 'X',
            'username': 'nomatch',
            'email': 'nomatch@test.com',
            'password1': 'SecurePass123!',
            'password2': 'DifferentPass123!',
        }), content_type='application/json')
        self.assertEqual(resp.status_code, 400)
        self.assertIn('password2', resp.data)

    def test_weak_password(self):
        resp = self.client.post(self.url, json.dumps({
            'first_name': 'X',
            'username': 'weakuser',
            'email': 'weak@test.com',
            'password1': '123',
            'password2': '123',
        }), content_type='application/json')
        self.assertEqual(resp.status_code, 400)


class LoginAPITest(APITestBase):
    def setUp(self):
        self.client = Client()
        self.url = '/api/auth/login/'
        self.user = User.objects.create_user('logintest', password='LoginPass123!')

    def test_successful_login(self):
        resp = self.client.post(self.url, json.dumps({
            'username': 'logintest',
            'password': 'LoginPass123!',
        }), content_type='application/json')
        self.assertEqual(resp.status_code, 200)
        self.assertIn('token', resp.data)
        self.assertEqual(resp.data['user']['username'], 'logintest')

    def test_wrong_password(self):
        resp = self.client.post(self.url, json.dumps({
            'username': 'logintest',
            'password': 'wrong',
        }), content_type='application/json')
        self.assertEqual(resp.status_code, 401)

    def test_nonexistent_user(self):
        resp = self.client.post(self.url, json.dumps({
            'username': 'nobody',
            'password': 'whatever',
        }), content_type='application/json')
        self.assertEqual(resp.status_code, 401)


class MeAPITest(APITestBase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('metest', email='me@test.com', password='MePass123!')
        self.token = Token.objects.create(user=self.user)
        self.url = '/api/auth/me/'

    def test_get_me(self):
        resp = self.client.get(self.url, HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data['username'], 'metest')
        self.assertEqual(resp.data['email'], 'me@test.com')
        self.assertIn('profile', resp.data)

    def test_unauthenticated(self):
        resp = self.client.get(self.url)
        self.assertIn(resp.status_code, [401, 403])


class InterestAPITest(APITestBase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('inttest', password='IntPass123!')
        self.token = Token.objects.create(user=self.user)

    def test_list_interests(self):
        resp = self.client.get('/api/interests/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data), 4)

    def test_select_interests(self):
        resp = self.client.post('/api/interests/select/',
            json.dumps({'interest_ids': [self.interest1.id, self.interest2.id]}),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data['interests']), 2)
        names = [i['name'] for i in resp.data['interests']]
        self.assertIn('Music', names)
        self.assertIn('Gaming', names)

    def test_select_invalid_interest(self):
        resp = self.client.post('/api/interests/select/',
            json.dumps({'interest_ids': [9999]}),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.assertEqual(resp.status_code, 400)

    def test_select_unauthenticated(self):
        resp = self.client.post('/api/interests/select/',
            json.dumps({'interest_ids': [1]}),
            content_type='application/json')
        self.assertIn(resp.status_code, [401, 403])


class MatchesAPITest(APITestBase):
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user('match_alice', password='Pass1234!')
        self.user2 = User.objects.create_user('match_bob', password='Pass1234!')
        self.p1, _ = Profile.objects.get_or_create(user=self.user1)
        self.p2, _ = Profile.objects.get_or_create(user=self.user2)
        self.p1.interests.set([self.interest1, self.interest2, self.interest3])
        self.p2.interests.set([self.interest1, self.interest2, self.interest4])
        self.token = Token.objects.create(user=self.user1)

    def test_matches_returns_shared(self):
        resp = self.client.get('/api/matches/',
            HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data), 1)
        m = resp.data[0]
        self.assertEqual(m['username'], 'match_bob')
        self.assertGreater(m['score'], 0)
        shared_names = [i['name'] for i in m['shared_interests']]
        self.assertIn('Music', shared_names)
        self.assertIn('Gaming', shared_names)

    def test_matches_unauthenticated(self):
        resp = self.client.get('/api/matches/')
        self.assertIn(resp.status_code, [401, 403])

    def test_matches_empty_when_no_overlap(self):
        self.p1.interests.set([self.interest3])
        self.p2.interests.set([self.interest4])
        resp = self.client.get('/api/matches/',
            HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.data), 0)
