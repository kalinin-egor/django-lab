from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from django.utils import timezone


class Tag(models.Model):
    name = models.CharField('Название', max_length=50, unique=True)
    slug = models.SlugField('URL-метка', max_length=50, unique=True)

    class Meta:
        ordering = ('name',)
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        indexes = [
            models.Index(fields=('name',), name='blog_tag_name_idx'),
        ]

    def __str__(self) -> str:
        return self.name


class PublishedManager(models.Manager):
    """Выбирает только опубликованные посты."""

    def get_queryset(self):
        return super().get_queryset().filter(status=Post.Status.PUBLISHED)


class Post(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'DF', 'Черновик'
        PUBLISHED = 'PB', 'Опубликован'

    title = models.CharField('Заголовок', max_length=250)
    slug = models.SlugField('URL-метка', max_length=250, unique_for_date='publish')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='blog_posts',
        verbose_name='Автор',
    )
    body = models.TextField('Содержимое')
    publish = models.DateTimeField('Дата публикации', default=timezone.now)
    created = models.DateTimeField('Создано', auto_now_add=True)
    updated = models.DateTimeField('Обновлено', auto_now=True)
    status = models.CharField(
        'Статус',
        max_length=2,
        choices=Status.choices,
        default=Status.DRAFT,
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги',
        related_name='posts',
        blank=True,
    )

    objects = models.Manager()
    published = PublishedManager()

    class Meta:
        ordering = ['-publish']
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'
        indexes = [
            models.Index(fields=['-publish'], name='blog_post_publish_idx'),
        ]

    def __str__(self) -> str:
        return self.title

    def get_absolute_url(self):
        return reverse(
            'blog:post_detail',
            args=[self.publish.year, self.publish.month, self.publish.day, self.slug],
        )


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Пост',
    )
    name = models.CharField('Имя', max_length=80)
    email = models.EmailField('Email')
    body = models.TextField('Комментарий')
    created = models.DateTimeField('Создано', auto_now_add=True)
    updated = models.DateTimeField('Обновлено', auto_now=True)
    active = models.BooleanField('Активен', default=True)

    class Meta:
        ordering = ('-created',)
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        indexes = [
            models.Index(fields=('created',), name='blog_comment_created_idx'),
            models.Index(fields=('active',), name='blog_comment_active_idx'),
        ]

    def __str__(self) -> str:
        return f"Комментарий от {self.name} к посту '{self.post}'"
