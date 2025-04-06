from wagtail.contrib.sitemaps.sitemap_generator import Sitemap
from wagtail.models import Page
from django.utils import timezone
from django.conf import settings  # Import settings to access SITE_URL

class CustomWagtailSitemap(Sitemap):
    def items(self):
        return Page.objects.live().public().specific()

    def location(self, item):
        # Use SITE_URL to generate the full URL dynamically
        try:
            protocol = 'https' if settings.USE_HTTPS else 'http'  # Use https if the setting is True
            domain = settings.SITE_URL  # Use SITE_URL defined in settings
            return f"{protocol}://{domain}{item.url}"  # Create full URL
        except Exception as e:
            return None

    def lastmod(self, item):
        return getattr(item, 'last_published_at', timezone.now())

    def changefreq(self, item):
        return "weekly"

    def priority(self, item):
        return 1.0 if item.slug == 'home' else 0.5

    def image_urls(self, item):
        if hasattr(item, "image") and item.image:
            return [item.image.file.url]
        elif hasattr(item, "gallery_images"):
            return [img.image.file.url for img in item.gallery_images.all() if img.image]
        return []
