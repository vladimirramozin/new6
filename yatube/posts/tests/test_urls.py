import time
from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from django.core.cache import cache
from posts.models import Post, Group

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=User.objects.create_user(username='Тест'),
            group=Group.objects.create(
                title='TITLE',
                slug='SLUG',
                description='DESCRIPTION'
            )
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.get(username='Тест')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/create_post.html': reverse('posts:post_create'),
            'posts/group_list.html': reverse('posts:group_list',
                                             kwargs={'slug': 'SLUG'}),
            'posts/profile.html': reverse('posts:profile',
                                          kwargs={'username': 'Тест'}),
            'posts/post_detail.html': reverse('posts:post_detail',
                                              args={self.post.id}),
            'posts/follow.html': reverse('posts:follow_index'),
        }

        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/group_list.html': reverse('posts:group_list',
                                             kwargs={'slug': 'SLUG'}),
            'posts/profile.html': reverse('posts:profile',
                                          kwargs={'username': 'Тест'}),
            'posts/post_detail.html': reverse('posts:post_detail',
                                              args={PostURLTests.post.id}),
            'posts/create_post.html': reverse('posts:post_create'),
        }
        for template, adress in templates_url_names.items():
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress)
                self.assertTemplateUsed(response, template)

    def test_custom_page_error_404(self):
        """Каст. ст. ошиьки 404 работает правильно"""
        response = self.client.get('something/really/')
        self.assertEqual(response.status_code, 404)
