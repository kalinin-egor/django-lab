from django.shortcuts import get_object_or_404, render

from .models import Post


def post_list(request):
    posts = (
        Post.published.select_related('author')
        .prefetch_related('tags')
        .order_by('-publish')
    )
    return render(request, 'blog/post/list.html', {'posts': posts})


def post_detail(request, year, month, day, post):
    post = get_object_or_404(
        Post.published.select_related('author').prefetch_related('tags'),
        publish__year=year,
        publish__month=month,
        publish__day=day,
        slug=post,
    )
    return render(request, 'blog/post/detail.html', {'post': post})
