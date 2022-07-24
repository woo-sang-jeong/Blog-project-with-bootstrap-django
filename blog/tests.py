from django.test import TestCase, Client
from bs4 import BeautifulSoup
from .models import Post

# Create your tests here.

class TestView(TestCase):
    def setUp(self):
        self.client = Client()

    def test_post_list(self):
        # 1.1 포스트 목록 페이지 가져오기
        response = self.client.get('/blog/')
        # 1.2 정상적으로 페이지 로드
        self.assertEqual(response.status_code, 200)
        # 1.3 페이지 타이틀은 'Blog'
        soup = BeautifulSoup(response.content, 'html.parser')
        #self.assertEqual(soup.title.test, 'Blog')
        # 1.4 내비게이션 바가 있다.
        navbar = soup.nav
        # 1.5 Blog, About me 라는 문구가 내비게이션 바에 있다.
        self.assertIn('Blog', navbar.text)
        self.assertIn('About Me', navbar.text)

        # 2.1  포스트가 없을시
        self.assertEqual(Post.objects.count(), 0)
        # 2.2 main area에 '아직 게시물이 없습니다' 라는 문구 보이기
        main_area = soup.find('div', id='main-area')
        self.assertIn('아직 게시물이 없습니다', main_area.text)

        # 3.1 포스트가 2개 있을시
        post_001 = Post.objects.create(
            title='첫 번째 포스트입니다',
            content='Hello World. we are the world',
        )
        post_002 = Post.objects.create(
            title='두 번째 포스트입니다',
            content='Hello Again',
        )
        self.assertEqual(Post.objects.count(), 2)

        # 3.2 포스트 목록 페이지를 새로고침했을 때
        response = self.client.get('/blog/')
        soup = BeautifulSoup(response.content, 'html.parser')
        self.assertEqual(response.status_code, 200)
        # 3.3 main area에 포스트 2개의 타이틀이 존재한다.
        main_area = soup.find('div', id='main-area')
        self.assertIn(post_001.title, main_area.text)
        self.assertIn(post_002.title, main_area.text)
        # 3.4 '아직 게시물이 없습니다' 라는 문구는 보이지 않음.
        self.assertNotIn('아직 게시물이 없습니다', main_area.text)