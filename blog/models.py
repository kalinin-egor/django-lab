from datetime import timedelta

from django.contrib.auth.models import User
from django.db import models
from django.db.models import Count, Max, Q
from django.urls import reverse
from django.utils import timezone


class PostStatus(models.TextChoices):
    DRAFT = 'DF', 'Черновик'
    PUBLISHED = 'PB', 'Опубликован'


class TagQuerySet(models.QuerySet):
    def with_post_counts(self):
        return self.annotate(
            published_posts=Count(
                'posts',
                filter=Q(posts__status=PostStatus.PUBLISHED),
                distinct=True,
            )
        )

    def with_latest_publish(self):
        return self.annotate(
            latest_publish=Max(
                'posts__publish',
                filter=Q(posts__status=PostStatus.PUBLISHED),
            )
        )


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

    objects = TagQuerySet.as_manager()

    def __str__(self) -> str:
        return self.name


class PostQuerySet(models.QuerySet):
    """Набор запросов с бизнес-логикой для работы с постами блога."""

    def published(self):
        return self.filter(status=Post.Status.PUBLISHED)

    def with_comment_counts(self):
        return self.annotate(
            comment_count=Count(
                'comments',
                filter=Q(comments__active=True),
                distinct=True,
            )
        )

    def trending(self, days=30, min_comments=1):
        threshold_date = timezone.now() - timedelta(days=days)
        return (
            self.published()
            .filter(publish__gte=threshold_date)
            .with_comment_counts()
            .filter(comment_count__gte=min_comments)
        )

    def for_search_term(self, term):
        return self.published().filter(
            Q(title__icontains=term)
            | Q(body__icontains=term)
            | Q(tags__name__icontains=term)
        ).distinct()

    def editors_choice(self):
        """Пример бизнес-правила: посты с тремя и более активными комментариями или с тегом 'featured'."""

        return (
            self.published()
            .with_comment_counts()
            .filter(
                Q(comment_count__gte=3)
                | Q(tags__slug__in=['featured', 'editor-choice'])
            )
            .distinct()
        )


class PostManager(models.Manager.from_queryset(PostQuerySet)):
    pass


class PublishedManager(PostManager):
    """Выбирает только опубликованные посты."""

    def get_queryset(self):
        return super().get_queryset().published()


class Post(models.Model):
    Status = PostStatus

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

    objects = PostManager()
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
