from django.shortcuts import render, get_object_or_404
from .models import Post


def BlogPage(request):
    posts = Post.objects.filter(on_main=True)
    return render(request, 'blog/blog.html', {'posts': posts})


def PostPage(request, slug):
    post = get_object_or_404(Post, slug=slug)
    more_posts = Post.objects.filter(on_main=True).exclude(id=post.id).order_by('-created_at')[:8]
    return render(request, 'blog/blog_article_details.html', {'post': post, 'more_posts': more_posts,})