from django.contrib.sitemaps import Sitemap
from django.urls import reverse

class StaticPagesSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8
    i18n = True

    def items(self):
        return [
            "home",
            "about",
            "contacts",
            "buyer",
            "delivery",
            "refund",
            "privacy",
            "offer",
            "prive-lab",
            "blog",
        ]

    def location(self, item):
        return reverse(item)

class BlogPostsSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.9
    i18n = True

    def items(self):
        from blog.models import Post
        return Post.objects.all()

    def lastmod(self, obj):
        for fld in ("updated_at", "updated", "modified", "published_at", "created"):
            if hasattr(obj, fld):
                return getattr(obj, fld)

    def location(self, obj):
        try:
            return obj.get_absolute_url()
        except Exception:
            from django.urls import reverse
            return reverse("post", kwargs={"slug": getattr(obj, "slug", "")})

SITEMAPS = {
    "static": StaticPagesSitemap,
    "blog":   BlogPostsSitemap,
}
