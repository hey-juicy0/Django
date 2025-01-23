from bs4 import BeautifulSoup
from django.test import TestCase,Client
from django.contrib.auth.models import User
from envs.jeewoo.DLLs.unicodedata import category

from single_pages.views import about_me
from .models import Post, Category

# Create your tests here.
class TestView(TestCase):
    def setUp(self):
        self.client = Client()

        post_001 = Post.objects.create(
            title = '첫 번째 포스트입니다.',
            content = 'Hello World. We are the world.',
            category = self.category_programming,
            author = self.user_trump
        )
        post_002 = Post.objects.create(
            title = '두 번째 포스트입니다.',
            content = '1등이 전부는 아니잖아요?',
            category = self.category_music,
            author = self.user_obama
        )
        post_003 = Post.objects.create(
            title='세 번째 포스트입니다.',
            content='category가 없을 수도 있죠',
            author=self.user_obama
        )

        self.user_trump = User.objects.create_user(username= 'trump', password='somepassword')
        self.user_obama = User.objects.create_user(username='obama', password='somepassword')

        self.category_programming = Category.objects.create(name='programming', slug='programming')
        self.category_music = Category.objects.create(name='music', slug='music')

    def category_card_test(self,soup):
        categories_card= soup.find('div', id = 'categories-card')
        self.assertIn(f'{self.category_programming.name} ({self.category_programming.post_set.count()})', categories_card.text)
        self.assertIn(f'{self.category_music.name} ({self.category_music.post_set.count()})', categories_card.text)
        self.assertIn(f'미분류 (1)', categories_card.text)

    def navbar_test(self,soup):
        navbar = soup.nav

        self.assertIn('Blog', navbar.text)
        self.assertIn('About Me', navbar.text)

        logo_btn = navbar.find('a', text = 'Jeewoo')
        self.assertEqual(logo_btn.attrs['href'], '/')

        home_btn = navbar.find('a', text = 'Home')
        self.assertEqual(home_btn.attrs['href'], '/')

        blog_btn = navbar.find('a', text = 'Blog')
        self.assertEqual(blog_btn.attrs['href'], '/blog/')

        about_me_btn = navbar.find ('a', text = 'About Me')
        self.assertEqual(about_me_btn.attrs['href'], '/about_me/')

    def test_post_list(self):
        self.assertEqual(Post.objects.count(), 3)

        response = self.client.get('/blog/')
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        self.navbar_test(soup)
        self.category_card_test(soup)

        main_area = soup.find('div', id = 'main-area')
        self.assertIn('아직 게시물이 없습니다', main_area.text)

        post_001_card = main_area.find('div', id = 'post-1')
        self.assertIn(self.post_001_card.title, post_001_card.text)
        self.assertIn(self.post_001_card.category.name, post_001_card.text)

        post_002_card = main_area.find('div', id='post-2')
        self.assertIn(self.post_002_card.title, post_002_card.text)
        self.assertIn(self.post_002_card.category.name, post_002_card.text)

        post_003_card = main_area.find('div', id = 'post-3')
        self.assertIn(self.post_003_card.title, post_003_card.text)
        self.assertIn(self.post_003_card.category.name, post_003_card.text)

        self.assertIn(self.user_trump.username.upper(), main_area.text)
        self.assertIn(self.user_obama.username.upper(), main_area.text)

        # 포스트가 없는 경우
        Post.objects.all().delete()
        self.assertEqual(Post.objects.count(), 0)
        response = self.client.get('/blog/')
        soup = BeautifulSoup(response.content, 'html.parser')
        main_area = soup.find('div', id = 'main-area')
        self.assertIn('아직 게시물이 없습니다.', main_area.text)

    def test_post_detail(self):
        post_001 = Post.objects.create(
            title = '첫 번째 포스트입니다.',
            content = 'Hello World. We are the world.',
            author = self.user_trump,
        )

        self.assertEqual(post_001.get_absolute_url(), '/blog/1/')

        response = self.client.get(post_001.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        self.navbar_test(soup)
        self.assertIn(post_001.title, soup.title.text)

        main_area = soup.find('div', id = 'main-area')
        post_area= main_area.find('div', id = 'post-area')
        self.assertIn(post_001.title, post_area.text)

        self.assertIn(self.user_trump.username.upper(), post_area.text)
        self.assertIn(post_001.content, post_area.text)