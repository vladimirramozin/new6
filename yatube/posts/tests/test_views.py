import shutil
import tempfile

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from posts.models import Comment, Follow, Group, Post

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )

        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=User.objects.create_user(username='Test'),
            image=uploaded,
            group=Group.objects.create(
                title='TITLE',
                slug='SLUG',
                description='DESCRIPTION'
            )
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.post.author,
            text='Тестовый текст'
        )

    def setUp(self):
        self.user = User.objects.get(username='Test')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.guest_client = Client()
        cache.clear()

    def test_post_create_show_correct_context(self):
        """Шаблон home сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_display_in_the_right_index_place(self):
        response = self.authorized_client.get(reverse('posts:index'))
        test_post = response.context.get('post')
        self.assertEqual(test_post, self.post)

    def test_display_in_the_right_place(self):
        response = (self.authorized_client.
                    get(reverse('posts:group_list',
                                kwargs={'slug': self.post.group.slug})))
        test_post = response.context.get('post')
        self.assertEqual(test_post, self.post)

    def test_display_in_the_right_place(self):
        response = self.authorized_client.get(
            reverse('posts:profile',
                    kwargs={'username': self.post.author}))
        test_post = response.context.get('post')
        self.assertEqual(test_post, self.post)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        task_text_0 = first_object.text
        task_group_0 = first_object.group
        self.assertEqual(task_text_0, 'Тестовый текст')
        self.assertEqual(task_group_0, self.post.group)

    def test_profile_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:profile',
                    kwargs={'username': self.post.author}))
        first_object = response.context['page_obj'][0]
        task_text_0 = first_object.text
        task_author_0 = first_object.author.username
        self.assertEqual(task_text_0, 'Тестовый текст')
        self.assertEqual(task_author_0, 'Test')

    def test_group_list_pages_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = (self.authorized_client.
                    get(reverse('posts:group_list', kwargs={'slug': 'SLUG'})))
        first_object = response.context['page_obj'][0]
        task_text_0 = first_object.text
        task_group_0 = first_object.group
        self.assertEqual(task_text_0, 'Тестовый текст')
        self.assertEqual(task_group_0, self.post.group)

    def test_post_edit_pages_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = (self.authorized_client.
                    get(reverse('posts:post_edit', args={self.post.id})))
        self.assertEqual(response.context.get('post').text, 'Тестовый текст')
        self.assertEqual(response.context.get('post').group, self.post.group)

    def test_show_comment(self):
        response = (self.authorized_client.get(reverse('posts:post_detail',
                    args={self.post.id})))
        self.assertEqual(response.context.get('comments').
                         get(text='Тестовый текст'),
                         self.comment)

    def test_create_comment_unauthorized_user(self):
        response = self.guest_client.get(reverse('posts:add_comment',
                                         args={self.post.id}))
        response.status_code
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('login') + '?next='
                             + reverse('posts:add_comment',
                             kwargs={'post_id': 1}))


class PaginatorTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        User.objects.create_user(username='Testi1'),
        Group.objects.create(
            title='TITLE1',
            slug='SLUG1',
            description='DESCRIPTION1'
        )
        posts = (Post(text=f'test{i}', author=User.objects.get(username='Testi1'),
                 group=Group.objects.get(title='TITLE1')) for i in range(13))
        Post.objects.bulk_create(posts, 13)

    def test_first_page_contains_ten_records(self):
        cache.clear()
        response = self.client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_contains_three_records(self):
        response = self.client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)


class FollowPagesTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.post2 = Post.objects.create(
            text='Тестовый текст',
            author=User.objects.create_user(username='Test2'),
            group=Group.objects.create(
                title='TITLE_subscriptions',
                slug='SLUG1_subscriptions',
                description='DESCRIPTIO_subscriptions'
            )
        )
        cls.user = User.objects.create_user(username='Test')

    def setUp(self):
        self.user = User.objects.get(username='Test')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.guest_client = Client()

    def test_user_subscriptions(self):
        """Авторизованный пользователь может подписаться"""
        self.authorized_client.get(reverse('posts:profile_follow',
                                   kwargs={'username': 'Test2'}))
        follow = Follow.objects.create(user=self.user, author = User.objects.get(username='Test2'))
        self.assertTrue(follow)

    def test_show_post_user_subscriptions(self):
        """У авторизо-го поль-я появляются посты поль-й, на ктр он подписан"""
        Follow.objects.create(user=self.user, author = User.objects.get(username='Test2'))
        response = self.authorized_client.get(reverse('posts:follow_index'))
        posts = response.context['page_obj'].object_list
        self.assertTrue(self.post2 in posts)
        self.assertTrue(self.post2.text == posts[0].text)
        self.assertTrue(self.post2.author == posts[0].author)
        self.assertTrue(self.post2.group == posts[0].group)        

    def test_show_post_user_unsubscriptions(self):
        """У неавториз. поль-ля не появляются посты"""
        Follow.objects.filter(user=self.user, author = User.objects.get(username='Test2')).delete()
        response = self.authorized_client.get(reverse('posts:follow_index'))
        posts = response.context['page_obj']
        self.assertEqual(posts, None)

    def test_user_subscriptions_delete(self):
        """Авторизованный пользователь может отписаться"""
        self.authorized_client.get(reverse('posts:profile_unfollow',
                                           kwargs={'username': 'Test2'}))
        follow = Follow.objects.filter(user=self.user).filter(
            author=self.post2.author)
        self.assertFalse(follow)


class CashTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.post3 = Post.objects.create(
            text='Тестовый текст для кеша',
            author=User.objects.create_user(username='Test3'),
            group=Group.objects.create(
                title='TITLE_cash',
                slug='TITLE_cash',
                description='TITLE_cash'
            )
        )

    def setUp(self):
        self.user = User.objects.get(username='Test3')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_cash(self):
        """проверяем контекст после удаления поста и""" 
        """после отчистки кеша"""
        response = self.authorized_client.get(reverse('posts:index'))
        test_context = response.context
        self.post3.delete()
        test_context_after_delete = response.context
        self.assertEqual(test_context, test_context_after_delete)
        cache.clear()
        test_context_after_delete_and_clear_cache = response.context
        self.assertFalse(test_context_after_delete_and_clear_cache)               
