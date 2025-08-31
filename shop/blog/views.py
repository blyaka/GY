from django.shortcuts import render, get_object_or_404
from .models import Post
from django.core.paginator import Paginator
from django.views.generic import ListView
from django.db.models import Q


def _page_links(paginator, current, window=1):
    last = paginator.num_pages
    if last <= 1:
        return [1]
    pages = [1]
    left = max(2, current - window)
    right = min(last - 1, current + window)
    if left > 2:
        pages.append('ellipsis')
    pages += list(range(left, current))
    if current not in (1, last):
        pages.append(current)
    pages += list(range(current + 1, right + 1))
    if right < last - 1:
        pages.append('ellipsis')
    pages.append(last)
    # схлопнуть двойные эллипсисы
    out = []
    for x in pages:
        if x == 'ellipsis' and out and out[-1] == 'ellipsis':
            continue
        out.append(x)
    return out

class BlogView(ListView):
    template_name = 'blog/blog.html'
    context_object_name = 'posts'
    paginate_by = 5

    def get_queryset(self):
        p = self.request.GET
        qs = Post.objects.filter(on_main=True).order_by('-created_at')

        q = (p.get('q') or '').strip()
        if q:
            qs = qs.filter(
                Q(title__icontains=q) |
                Q(content__icontains=q)
            )

        # если будут категории/теги — докинешь сюда, как в ShopView
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        p = self.request.GET.copy()
        if 'page' in p:
            p.pop('page')
        ctx['querystring'] = p.urlencode()

        pg = ctx['page_obj'].paginator
        ctx['page_links'] = _page_links(pg, ctx['page_obj'].number, window=1)
        return ctx

def PostPage(request, slug):
    post = get_object_or_404(Post, slug=slug)
    more_posts = Post.objects.filter(on_main=True).exclude(id=post.id).order_by('-created_at')[:8]
    return render(request, 'blog/blog_article_details.html', {'post': post, 'more_posts': more_posts,})