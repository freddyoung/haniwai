from wagtail.models import Site
from .models import ResourcesIndexPage # Ensure this import path is correct for your ResourcesIndexPage model

def resources_index_page(request):
    # Get the current site based on the request
    site = Site.find_for_request(request)
    if site:
        # Get the root page of the site
        root_page = site.root_page
        # Find the first live ResourcesIndexPage among the root's children
        resources_index_page = root_page.get_children().type(ResourcesIndexPage).live().first()
        return {'resources_index_page': resources_index_page}
    return {}

from wagtail.models import Site
from .models import AboutPage, EventsPage, GalleryPage, ContactPage, DonatePage, ResourcesIndexPage

def common_pages(request):
    site = Site.find_for_request(request)
    if site:
        root_page = site.root_page
        return {
            'about_page': root_page.get_children().type(AboutPage).live().first(),
            'news_events_page': root_page.get_children().type(EventsPage).live().first(),
            'gallery_page': root_page.get_children().type(GalleryPage).live().first(),
            'contact_page': root_page.get_children().type(ContactPage).live().first(),
            'donate_page': root_page.get_children().type(DonatePage).live().first(),
            'resources_index_page': root_page.get_children().type(ResourcesIndexPage).live().first(),
        }
    return {}