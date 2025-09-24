from django.contrib import admin

from .models import Comment, Post, Tag


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    fields = ('name', 'email', 'body_preview', 'active', 'created', 'updated')
    readonly_fields = ('body_preview', 'created', 'updated')
    show_change_link = True

    @admin.display(description='Предпросмотр')
    def body_preview(self, obj):
        if not obj or not obj.body:
            return '—'
        text = obj.body
        return text[:60] + ('…' if len(text) > 60 else '')


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    date_hierarchy = 'publish'
    list_display = (
        'title',
        'author',
        'publish',
        'status',
        'display_tags',
    )
    list_display_links = ('title', 'author')
    list_filter = ('status', 'created', 'publish', 'author', 'tags')
    search_fields = ('title', 'body', 'tags__name')
    prepopulated_fields = {'slug': ('title',)}
    raw_id_fields = ('author',)
    readonly_fields = ('created', 'updated', 'tag_summary')
    filter_horizontal = ('tags',)
    inlines = (CommentInline,)

    fieldsets = (
        ('Основная информация', {'fields': ('title', 'slug', 'author', 'status')}),
        (
            'Содержимое и теги',
            {'fields': ('body', 'tags', 'tag_summary')},
        ),
        (
            'Временные метки',
            {
                'fields': ('publish', 'created', 'updated'),
            },
        ),
    )

    @admin.display(description='Теги')
    def display_tags(self, obj):
        tag_names = list(obj.tags.values_list('name', flat=True))
        return ', '.join(tag_names) if tag_names else '—'

    @admin.display(description='Подборка тегов')
    def tag_summary(self, obj):
        if not obj:
            return '—'
        return self.display_tags(obj)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    date_hierarchy = 'created'
    list_display = ('name', 'email', 'post', 'created', 'active', 'short_body')
    list_display_links = ('name', 'post')
    list_filter = ('active', 'created', 'updated', 'post__author')
    search_fields = ('name', 'email', 'body', 'post__title')
    raw_id_fields = ('post',)
    readonly_fields = ('created', 'updated')

    @admin.display(description='Текст', ordering='body')
    def short_body(self, obj):
        if not obj.body:
            return '—'
        return obj.body[:40] + ('…' if len(obj.body) > 40 else '')


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'post_count')
    list_display_links = ('name',)
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

    @admin.display(description='Количество постов')
    def post_count(self, obj):
        return obj.posts.count()
