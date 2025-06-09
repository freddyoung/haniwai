from django.conf import settings
from django.urls import include, path
from django.contrib import admin
from django.views.generic import TemplateView
from wagtail.admin import urls as wagtailadmin_urls
from wagtail import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls
from search import views as search_views

from django.contrib.sitemaps.views import sitemap as django_sitemap_view
from django.http import HttpResponse
from home.sitemaps import FinalHaniwaiSitemap

# Custom sitemap view to remove the X-Robots-Tag header
def sitemap_view(request):
    response = django_sitemap_view(request, sitemaps={"wagtail": FinalHaniwaiSitemap})
    response["Content-Type"] = "application/xml"
    if "X-Robots-Tag" in response:
        del response["X-Robots-Tag"]
    return response

urlpatterns = [
    path("django-admin/", admin.site.urls),
    path("admin/", include(wagtailadmin_urls)),
    path("documents/", include(wagtaildocs_urls)),
    path("search/", search_views.search, name="search"),
    path("robots.txt", TemplateView.as_view(template_name="robots.txt", content_type="text/plain")),
    path("sitemap.xml", sitemap_view, name="sitemap"),
]

if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += [
    path("", include(wagtail_urls)),
]
