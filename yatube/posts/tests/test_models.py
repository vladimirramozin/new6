from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Post, Group

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая группа',
        )

    def test_models_have_correct_object_names(self):
        test_group = PostModelTest.group
        expected_object_name = test_group.title
        self.assertEqual(expected_object_name, str(test_group))
        test_post = PostModelTest.post
        expected_object_names = test_post.text[:15]
        self.assertEqual(expected_object_names, str(test_post))
