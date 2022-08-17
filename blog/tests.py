from django.test import TestCase, Client
from bs4 import BeautifulSoup
from django.contrib.auth.models import User
from .models import Post, Category, Tag


# Create your tests here.

class TestView(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_jus = User.objects.create_user(username='jus', password='123123')
        self.user_woosang = User.objects.create_user(username='woosang', password='123456')
        self.user_jus.is_staff = True
        self.user_jus.save()

        self.category_programming = Category.objects.create(name='programming', slug='programming')
        self.category_music = Category.objects.create(name='music', slug='music')

        self.tag_python = Tag.objects.create(name='python', slug='python')
        self.tag_bootstrap = Tag.objects.create(name='bootstrap', slug='bootstrap')
        self.tag_django = Tag.objects.create(name='django', slug='django')

        self.post_001 = Post.objects.create(
            title='첫 번째 포스트 입니다',
            content='Hello World. we are the world',
            category=self.category_programming,
            author=self.user_jus
        )
        self.post_001.tags.add(self.tag_python)

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
        self.post_003.tags.add(self.tag_bootstrap)
        self.post_003.tags.add(self.tag_django)

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

        # id가 post-1,2,3인 div 요소에 제목과, 카테고리, 작가, 연결된 태그만 존재하는가?
        post_001_card = main_area.find('div', id='post-1')
        self.assertIn(self.post_001.title, post_001_card.text)
        self.assertIn(self.post_001.category.name, post_001_card.text)
        self.assertIn(self.post_001.author.username.upper(), post_001_card.text)
        self.assertIn(self.tag_python.name, post_001_card.text)
        self.assertNotIn(self.tag_bootstrap.name, post_001_card.text)
        self.assertNotIn(self.tag_bootstrap.name, post_001_card.text)

        post_002_card = main_area.find('div', id='post-2')
        self.assertIn(self.post_002.title, post_002_card.text)
        self.assertIn(self.post_002.category.name, post_002_card.text)
        self.assertNotIn(self.tag_python.name, post_002_card.text)
        self.assertNotIn(self.tag_bootstrap.name, post_002_card.text)
        self.assertNotIn(self.tag_django.name, post_002_card.text)

        post_003_card = main_area.find('div', id='post-3')
        self.assertIn('미분류', post_003_card.text)
        self.assertIn(self.post_003.title, post_003_card.text)
        self.assertIn(self.tag_bootstrap.name, post_003_card.text)
        self.assertIn(self.tag_django.name, post_003_card.text)
        self.assertNotIn(self.tag_python.name, post_003_card.text)

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
        main_area = soup.find('div', id='main-area')

        # 포스트가 없는 경우를 테스트 하므로 '아직 게시물이 없습니다' 문구가 main_area에 있어야 한다.
        self.assertIn('아직 게시물이 없습니다', main_area.text)

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

        # 태그가 포스트 상세 페이지에 존재하는가?
        self.assertIn(self.tag_python.name, post_area.text)
        self.assertNotIn(self.tag_bootstrap.name, post_area.text)
        self.assertNotIn(self.tag_django.name, post_area.text)

    def test_category_page(self):
        # 카테고리 페이지의 고유 URL을 통해 정상적으로 접속되는지 확인한다.
        response = self.client.get(self.category_programming.get_absolute_url())
        self.assertEqual(response.status_code, 200)

        # BeautifulSoup로 html을 다루기 쉽게 파싱하고 내비게이션바, 카테고리 카드가 제대로 구성되었는지 확인한다.
        soup = BeautifulSoup(response.content, 'html.parser')
        self.navbar_test(soup)
        self.category_card_test(soup)

        # 상단의 카테고리 뱃지가 나오는지 확인한다. 페이지에 <h1>태그는 하나밖에 없으므로 태그에 카테고리 이름이 있는지 확인한다.
        # 카테고리 이름인 programming 있는지 확인한다. 카테고리 이름이 다르거나 없는 post 2,3은 main_area에 없어야 한다.
        main_area = soup.find('div', id='main-area')
        self.assertIn(self.category_programming.name, main_area.h1.text)
        self.assertIn(self.category_programming.name, main_area.text)
        self.assertIn(self.post_001.title, main_area.text)
        self.assertNotIn(self.post_002.title, main_area.text)
        self.assertNotIn(self.post_003.title, main_area.text)

    def test_tag_page(self):
        response = self.client.get(self.tag_python.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        self.navbar_test(soup)
        self.category_card_test(soup)

        main_area = soup.find('div', id='main-area')
        self.assertIn(self.tag_python.name, main_area.h1.text)
        self.assertIn(self.tag_python.name, main_area.text)
        self.assertIn(self.post_001.title, main_area.text)
        self.assertNotIn(self.post_002.title, main_area.text)
        self.assertNotIn(self.post_003.title, main_area.text)

    def test_create_post(self):
        response = self.client.get('/blog/create_post/')
        self.assertNotEqual(response.status_code, 200)

        # staff가 아닌 woosang이 로그인
        self.client.login(username='woosang', password='123456')
        response = self.client.get('/blog/create_post/')
        self.assertNotEqual(response.status_code, 200)

        # staff인 jus가 로그인
        self.client.login(username='jus', password='123123')

        response = self.client.get('/blog/create_post/')
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        self.assertEqual('Create Post - Blog', soup.title.text)
        main_area = soup.find('div', id='main-area')
        self.assertIn('Create New Post', main_area.text)

        # 첫번째 인수로 URL, 두번째 인수로 딕셔너리 안의 정보를 POST 방식으로 보낸다.
        self.client.post(
            '/blog/create_post/',
            {
                'title': 'Post Form 만들기',
                'content': 'Post Form 페이지 만들기',
            }
        )
        self.assertEqual(Post.objects.count(), 4)
        # Post.objects.last()로 마지막 Post 레코드를 가져와 last_post 변수에 저장하고 제목이 일치한지 확인한다.
        # 작성자와 작성시간 필드는 자동으로 채워지게 views.py에 구현한다.
        last_post = Post.objects.last()
        self.assertEqual(last_post.title, "Post Form 만들기")
        self.assertEqual(last_post.author.username, 'jus')

    def test_update_post(self):
        # URL 형태는 /blog/update_post/포스트.pk
        update_post_url = f'/blog/update_post/{self.post_003.pk}/'

        # 비로그인 상황
        response = self.client.get(update_post_url)
        self.assertNotEqual(response.status_code, 200)

        # 로그인 상황(작성자 X), 403 code는 권한이 없는 경우
        self.assertNotEqual(self.post_003.author, self.user_woosang)
        self.client.login(
            username=self.user_woosang.username,
            password='123456'
        )
        response = self.client.get(update_post_url)
        self.assertEqual(response.status_code, 403)

        # 로그인 상황(작성자 O)
        self.client.login(
            username=self.post_003.author.username,
            password='123123'
        )
        response = self.client.get(update_post_url)
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        # 타이틀이 Edit Post - Blog 인지, 메인영역에 Edit Post가 있는지 확인
        # 문제 없을시 title, content, category 값을 수정 후 POST 방식으로 update_post_url에 보낸다.
        self.assertEqual('Edit Post - Blog', soup.title.text)
        main_area = soup.find('div', id='main-area')
        self.assertIn('Edit Post', main_area.text)

        response = self.client.post(
            update_post_url,
            {
                'title': '세 번째 포스트 수정',
                'content': 'hi world',
                'category': self.category_music.pk
            },
            follow=True
        )
        # title, content, category가 제대로 수정 되었는지 확인
        soup = BeautifulSoup(response.content, 'html.parser')
        main_area = soup.find('div', id='main-area')
        self.assertIn('세 번째 포스트 수정', main_area.text)
        self.assertIn('hi world', main_area.text)
        self.assertIn(self.category_music.name, main_area.text)




