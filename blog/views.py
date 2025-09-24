from django.db.models import Count, Max
from django.shortcuts import get_object_or_404, render

from .forms import SearchForm
from .models import Comment, Post, Tag


def home(request):
    search_form = SearchForm()

    latest_posts = (
        Post.published.select_related('author')
        .prefetch_related('tags')
        .order_by('-publish')[:5]
    )

    trending_posts = (
        Post.objects.trending(days=30, min_comments=1)
        .select_related('author')
        .prefetch_related('tags')
        .order_by('-comment_count', '-publish')[:5]
    )

    editors_choice = (
        Post.objects.editors_choice()
        .select_related('author')
        .prefetch_related('tags')
        .order_by('-publish')[:5]
    )

    top_tags = (
        Tag.objects.with_post_counts()
        .with_latest_publish()
        .filter(published_posts__gt=0)
        .order_by('-published_posts', '-latest_publish', 'name')[:10]
    )

    active_commenters = (
        Comment.objects.filter(active=True)
        .values('name', 'email')
        .annotate(
            comments_total=Count('id'),
            recent_comment=Max('created'),
        )
        .order_by('-comments_total', '-recent_comment')[:5]
    )

    context = {
        'search_form': search_form,
        'latest_posts': latest_posts,
        'trending_posts': trending_posts,
        'editors_choice': editors_choice,
        'top_tags': top_tags,
        'active_commenters': active_commenters,
    }

    return render(request, 'blog/home.html', context)


def post_list(request):
    tag_slug = request.GET.get('tag')
    posts = Post.published.select_related('author').prefetch_related('tags')

    active_tag = None
    if tag_slug:
        active_tag = get_object_or_404(Tag, slug=tag_slug)
        posts = posts.filter(tags__slug=tag_slug)

    posts = posts.order_by('-publish')
    return render(
        request,
        'blog/post/list.html',
        {
            'posts': posts,
            'search_form': SearchForm(),
            'active_tag': active_tag,
        },
    )


def post_detail(request, year, month, day, post):
    post = get_object_or_404(
        Post.published.select_related('author').prefetch_related('tags'),
        publish__year=year,
        publish__month=month,
        publish__day=day,
        slug=post,
    )

    comments = (
        post.comments.filter(active=True)
        .select_related('post')
        .order_by('-created')
    )

    related_posts = (
        Post.objects.with_comment_counts()
        .filter(tags__in=post.tags.all())
        .exclude(id=post.id)
        .published()
        .order_by('-comment_count', '-publish')
        .distinct()[:3]
    )
    return render(
        request,
        'blog/post/detail.html',
        {
            'post': post,
            'comments': comments,
            'related_posts': related_posts,
            'search_form': SearchForm(),
        },
    )


def search_posts(request):
    form = SearchForm(request.GET or None)
    results = Post.objects.none()
    query = ''

    if form.is_valid():
        query = form.cleaned_data['q']
        if query:
            results = (
                Post.objects.for_search_term(query)
                .select_related('author')
                .prefetch_related('tags')
                .order_by('-publish')
            )

    context = {
        'form': form,
        'query': query,
        'results': results,
        'search_form': form,
    }
    return render(request, 'blog/search_results.html', context)
