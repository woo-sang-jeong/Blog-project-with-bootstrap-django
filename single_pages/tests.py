from django.test import TestCase, Client
from django.contrib.auth.models import User
from bs4 import BeautifulSoup
from blog.models import Post

# Create your tests here.

class TestView(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_jus = User.objects.create_user(username='jus', password='123123')

    def test_landing(self):
        post_001 = Post.objects.create(
            title='Post 1',
            content='1',
            author=self.user_jus
        )

        post_002 = Post.objects.create(
            title='Post 2',
            content='2',
            author=self.user_jus
        )

        post_003 = Post.objects.create(
            title='Post 3',
            content='3',
            author=self.user_jus
        )

        post_004 = Post.objects.create(
            title='Post 4',
            content='4',
            author=self.user_jus
        )

        response = self.client.get('')
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        body = soup.body
        self.assertNotIn(post_001.title, body.text)
        self.assertIn(post_002.title, body.text)
        self.assertIn(post_003.title, body.text)
        self.assertIn(post_004.title, body.text)



