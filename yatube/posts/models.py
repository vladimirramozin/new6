from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin

User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200, verbose_name='Заголовок группы')
    slug = models.SlugField(unique=True)
    description = models.TextField(verbose_name='Описание группы')

    class Meta:
        verbose_name = 'группа'
        verbose_name_plural = 'группы'
        default_related_name = 'groups'

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(verbose_name='Текст')
    pub_date = models.DateTimeField(auto_now_add=True, verbose_name='Дата')
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name='группа',
        related_name='posts'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='автор'
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    def __str__(self):
        return self.text[:15]

    class Meta:
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'
        default_related_name = 'posts'
        ordering = ('-pub_date',)


class Comment(models.Model, LoginRequiredMixin):
    post = models.ForeignKey(Post,
                             on_delete=models.CASCADE,
                             related_name='comments')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='автор'
    )
    text = models.TextField(verbose_name='Текст')
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('created',)
        verbose_name_plural = 'Коментарии'


class Follow(models.Model):
    user = models.ForeignKey(User,
                             blank=True,
                             null=True,
                             on_delete=models.CASCADE,
                             related_name='follower')
    author = models.ForeignKey(User,
                               blank=True,
                               null=True,
                               on_delete=models.CASCADE,
                               related_name='following')
    class Meta:
        verbose_name_plural = 'Подписки'