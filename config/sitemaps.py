from django.contrib.sitemaps import Sitemap
from django.urls import reverse


class StaticViewSitemap(Sitemap):
    priority = 0.8
    changefreq = "weekly"

    def items(self):
        # Only pages reachable without login — teacher/offering detail pages
        # require auth and can't be crawled/indexed as they stand.
        return ["home", "map"]

    def location(self, item):
        return reverse(item)
