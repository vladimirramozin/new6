import shutil
import tempfile

from posts.models import Post, Group
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse


User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='Test')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_create_post(self):
        tasks_count = Post.objects.count()
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
        form_data = {
            'text': 'Test',
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data
        )

        self.assertRedirects(response, reverse('posts:profile',
                             kwargs={'username': 'Test'}))
        self.assertEqual(Post.objects.count(), tasks_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text='Test',
                image='posts/small.gif'
            ).exists()
        )

    def test_edit_post(self):
        @classmethod
        def setUpClass(cls):
            super().setUpClass()
            cls.post = Post.objects.create(
                text='Тестовый текст',
                author=User.objects.get(username='Test'),
                group=Group.objects.create(
                    title='TITLE',
                    slug='SLUG',
                    description='DESCRIPTION'
                )
            )

        def test_update_result(self):
            obj = self.post
            Post.objects.filter(pk=obj.pk).update(text='abc')
            obj.refresh_from_db()
            self.assertEqual(obj.text, 'abc')
