from wagtail.contrib.sitemaps.sitemap import Sitemap
from django.conf import settings


class FinalHaniwaiSitemap(Sitemap):
    def get_urls(self, site=None, **kwargs):
        urls = super().get_urls(site=site, **kwargs)
        for url in urls:
            loc = url.get("location", "")
            if loc.startswith("http://") and getattr(settings, "USE_HTTPS", False):
                url["location"] = loc.replace("http://", "https://", 1)
            print("🛰 Sitemap entry:", url["location"])  # For Render logs
        return urls
