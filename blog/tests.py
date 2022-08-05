from django.test import TestCase, Client
from bs4 import BeautifulSoup
from django.contrib.auth.models import User
from .models import Post, Category


# Create your tests here.

class TestView(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_jus = User.objects.create_user(username='jus', password='wltn145890!')
        self.user_woosang = User.objects.create_user(username='woosang', password='wltn145890!')

        self.category_programming = Category.objects.create(name='programming', slug='programming')
        self.category_music = Category.objects.create(name='music', slug='music')

        self.post_001 = Post.objects.create(
            title='첫 번째 포스트 입니다',
            content='Hello World. we are the world',
            category=self.category_programming,
            author=self.user_jus
        )
        self.post_002 = Post.objects.create(
            title='두 번째 포스트 입니다',
            content='Hello Again',
            category=self.category_music,
            author=self.user_woosang
        )
        self.post_003 = Post.objects.create(
            title='세 번째 포스트 입니다.',
            content='none category',
            author=self.user_jus
        )

    def category_card_test(self, soup):
        categories_card = soup.find('div', id='categories-card')
        self.assertIn('Categories', categories_card.text)
        self.assertIn(
            f'{self.category_programming} ({self.category_programming.post_set.count()})',
            categories_card.text
        )
        self.assertIn(
            f'{self.category_music} ({self.category_music.post_set.count()})',
            categories_card.text
        )
        self.assertIn(
            f'미분류 ({Post.objects.filter(category=None).count()})',
            categories_card.text
        )

    def navbar_test(self, soup):
        navbar = soup.nav
        self.assertIn('Blog', navbar.text)
        self.assertIn('About Me', navbar.text)

        logo_btn = navbar.find('a', text='Do It Django')
        self.assertEqual(logo_btn.attrs['href'], '/')

        home_btn = navbar.find('a', text='Home')
        self.assertEqual(home_btn.attrs['href'], '/')

        blog_btn = navbar.find('a', text='Blog')
        self.assertEqual(blog_btn.attrs['href'], '/blog/')

        about_me_btn = navbar.find('a', text='About Me')
        self.assertEqual(about_me_btn.attrs['href'], '/about_me/')

    def test_post_list(self):
        # 포스트가 있는 경우

        # setUp()함수에서 만든 포스트가 3개인가?
        self.assertEqual(Post.objects.count(), 3)

        # 클라이언트가 정상적인 상태 코드 200을 내뱉는가?
        response = self.client.get('/blog/')
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        # 내비,카테고리 카드 테스트
        self.navbar_test(soup)
        self.category_card_test(soup)

        # id가 main_area인 div 요소에 '아직 게시물이 없습니다' 문구가 존재해서는 안 된다.
        main_area = soup.find('div', id='main-area')
        self.assertNotIn('아직 게시물이 없습니다', main_area.text)

        # id가 post-1,2,3인 div 요소에 제목과, 카테고리가 존재하는가?
        post_001_card = main_area.find('div', id='post-1')
        self.assertIn(self.post_001.title, post_001_card.text)
        self.assertIn(self.post_001.category.name, post_001_card.text)

        post_002_card = main_area.find('div', id='post-2')
        self.assertIn(self.post_002.title, post_002_card.text)
        self.assertIn(self.post_002.category.name, post_002_card.text)

        post_003_card = main_area.find('div', id='post-3')
        self.assertIn('미분류', post_003_card.text)
        self.assertIn(self.post_003.title, post_003_card.text)

        # jus, woosang user가 main_area에 있는가?
        self.assertIn(self.user_jus.username.upper(), main_area.text)
        self.assertIn(self.user_woosang.username.upper(), main_area.text)

        # 포스트가 없는 경우
        # 포스트 모두 삭제
        Post.objects.all().delete()

        # 포스트가 없는 경우 이므로 포스트는 0개 이여야 한다.
        self.assertEqual(Post.objects.count(), 0)
        response = self.client.get('/blog/')
        soup = BeautifulSoup(response.content, 'html.parser')
        main_area = soup.find('div', id='main_area')

        # 포스트가 없는 경우를 테스트 하므로 '아직 게시물이 없습니다' 문구가 main_area에 있어야 한다.
        #self.assertIn('아직 게시물이 없습니다', main_area.text)

    def test_post_detail(self):

        # 포스트의 url은 '/blog/1/' 이다.
        self.assertEqual(self.post_001.get_absolute_url(), '/blog/1/')

        # 첫 번째 포스트의 상세 페이지 테스트
        # 첫 번째 포스트의 url로 접근하면 정상적으로 작동 (status code: 200)
        response = self.client.get(self.post_001.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        # navbar_text 함수에서 테스트 한다.
        self.navbar_test(soup)
        # 카테고리 테스트 함수 호출
        self.category_card_test(soup)
        # 포스트의 제목이 웹 브라우저 탭 타이틀에 들어있다.
        self.assertIn(self.post_001.title, soup.title.text)
        # 포스트의 제목이 포스트 영역에 있다.
        main_area = soup.find('div', id='main-area')
        post_area = main_area.find('div', id='post-area')
        self.assertIn(self.post_001.title, post_area.text)
        self.assertIn(self.category_programming.name, post_area.text)
        # 첫 번째 포스트의 작성자가 포스트 영역에 있다.
        self.assertIn(self.user_jus.username.upper(), post_area.text)
        # 포스트의 내용이 포스트 영역에 있다.
        self.assertIn(self.post_001.content, post_area.text)
