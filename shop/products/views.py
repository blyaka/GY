
from django.views.generic import ListView, DetailView
from django.db.models import Q, Subquery, OuterRef
from django.db.models.functions import Coalesce
from django.core.paginator import Paginator, EmptyPage
from .models import Product, ProductImage, Category, Color, Size, ProductFabric
from django.http import JsonResponse, Http404
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_GET
from django.db.models import Prefetch




ORDER_MAP = {
    'price_asc': ('price', 'id'),
    'price_desc': ('-price', 'id'),
    'new': ('-id',),
    'name': ('name', 'id'),
}


def _get_thumb_subq():
    featured = ProductImage.objects.filter(
        product=OuterRef('pk'), is_featured=True
    ).order_by('id').values('id')[:1]

    first = ProductImage.objects.filter(
        product=OuterRef('pk')
    ).order_by('order', 'id').values('id')[:1]

    return Coalesce(Subquery(featured), Subquery(first))




class ShopView(ListView):
    template_name = 'shop/shop.html'
    context_object_name = 'items'
    paginate_by = 12

    def get_queryset(self):
        p = self.request.GET

        qs = (Product.objects
              .select_related('category')
              .prefetch_related('colors', 'sizes', 'images')
              .annotate(thumb_id=_get_thumb_subq())
              )

        q = (p.get('q') or '').strip()
        if q:
            qs = qs.filter(
                Q(name__icontains=q) |
                Q(article__icontains=q) |
                Q(description__icontains=q)
            )

        cat = p.get('category')
        if cat:
            qs = qs.filter(category_id=cat)

        color_ids = p.getlist('color')
        if color_ids:
            qs = qs.filter(colors__id__in=color_ids)

        size_ids = p.getlist('size')
        if size_ids:
            qs = qs.filter(sizes__id__in=size_ids)

        # Цена
        price_min = p.get('price_min')
        if price_min and price_min.isdigit():
            qs = qs.filter(price__gte=int(price_min))

        price_max = p.get('price_max')
        if price_max and price_max.isdigit():
            qs = qs.filter(price__lte=int(price_max))

        # Сортировка
        order_key = p.get('order') or 'new'
        qs = qs.order_by(*ORDER_MAP.get(order_key, ORDER_MAP['new']))

        if color_ids or size_ids:
            qs = qs.distinct()

        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        p = self.request.GET
        ctx['categories'] = Category.objects.only('id', 'name').order_by('name')
        ctx['colors'] = Color.objects.only('id', 'name', 'hex_code').order_by('name')
        ctx['sizes'] = Size.objects.only('id', 'name').order_by('name')

        ctx['q'] = p.get('q', '')
        ctx['order'] = p.get('order', 'new')
        ctx['price_min'] = p.get('price_min', '')
        ctx['price_max'] = p.get('price_max', '')
        ctx['selected'] = {
            'category': p.get('category', ''),
            'colors': p.getlist('color'),
            'sizes': p.getlist('size'),
        }
        return ctx








@require_GET
def quick_view(request, pk: int):
    qs = (
        Product.objects
        .select_related('category')  # если у тебя поле называется иначе — поправь
        .prefetch_related(
            'colors',
            'sizes',
            Prefetch('images', queryset=ProductImage.objects.order_by('-is_featured', 'id')),
            Prefetch('fabrics', queryset=ProductFabric.objects.select_related('fabric')),
        )
    )
    p = get_object_or_404(qs, pk=pk)

    # главное фото (featured → иначе первое), безопасно берём url
    im = next(iter(p.images.all()), None)
    img_url = None
    if im and getattr(im, 'image', None):
        try:
            img_url = im.image.url
        except Exception:
            img_url = None

    data = {
        "id": p.id,
        "name": p.name,
        "article": p.article,
        "price": p.price,
        "image": img_url,
        "category": {"id": p.category_id, "name": getattr(p.category, "name", "")} if hasattr(p, "category") else None,
        "colors": [{"id": c.id, "name": c.name, "hex": c.hex_code} for c in p.colors.all()],
        "sizes": [{"id": s.id, "name": s.name} for s in p.sizes.all()],
        "fabrics": [{"name": pf.fabric.name, "pct": pf.percentage} for pf in p.fabrics.all()],
    }
    return JsonResponse(data)




class ProductDetailView(DetailView):
    model = Product
    template_name = "shop/product_detail.html"
    context_object_name = "product"