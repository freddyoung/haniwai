from django.db import models
from wagtail.models import Page
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, InlinePanel, PageChooserPanel
from wagtail.fields import RichTextField
from wagtail.images.models import Image
from modelcluster.fields import ParentalKey





class HomePage(Page):
    """Custom Home Page"""
    template = "home/home_page.html"
    welcome_text = models.CharField(max_length=255, default="Welcome to Our NGO")

    # ✅ NEW: Links to the Gallery Page
    gallery_page = models.ForeignKey(
        "home.GalleryPage",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+"
    )

    content_panels = Page.content_panels + [
        FieldPanel("welcome_text"),
        PageChooserPanel("gallery_page"),  # ✅ Allows linking to the gallery page
        MultiFieldPanel([
            InlinePanel("gallery_images", label="Gallery Images"),
        ], heading="Gallery Section"),
    ]

from django.core.paginator import Paginator
from django.db.models import Q

def get_context(self, request):
    context = super().get_context(request)

    homepage = HomePage.objects.first()
    images = homepage.gallery_images.all()

    # Search Logic
    query = request.GET.get("q")
    if query:
        images = images.filter(
            Q(image__title__icontains=query) |
            Q(image__tags__name__icontains=query) |
            Q(image__description__icontains=query)
        ).distinct()

    # Pagination
    paginator = Paginator(images, 20)  # 20 per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context["gallery_images"] = page_obj
    context["query"] = query

    return context



class GalleryImage(models.Model):
    """Gallery Images for HomePage"""
    page = ParentalKey("home.HomePage", on_delete=models.CASCADE, related_name="gallery_images")
    image = models.ForeignKey(Image, on_delete=models.CASCADE, related_name="+")
    caption = models.CharField(max_length=255, blank=True, null=True)

    panels = [
        FieldPanel("image"),
        FieldPanel("caption"),
    ]

    def __str__(self):
        return self.caption if self.caption else "Gallery Image"


class GalleryPage(Page):
    """Gallery Page - Displays All Images"""
    template = "home/gallery_page.html"
    description = RichTextField(blank=True, null=True)

    content_panels = Page.content_panels + [
        FieldPanel("description"),
    ]

    def get_context(self, request):
        context = super().get_context(request)

        # Get gallery images from HomePage (assumes only one homepage)
        homepage = HomePage.objects.first()
        images = homepage.gallery_images.select_related('image').all()
        search_query = request.GET.get('q')
        if search_query:
            images = images.filter(
                models.Q(image__title__icontains=search_query) |
                models.Q(caption__icontains=search_query)
            )
        context["gallery_images"] = images

        return context


class AboutPage(Page):
    """About Us Page"""
    template = "home/about_page.html"
    description = RichTextField()

    content_panels = Page.content_panels + [
        FieldPanel("description"),
    ]


class EventsPage(Page):
    """Events Page"""
    template = "home/events_page.html"
    events_description = RichTextField()

    content_panels = Page.content_panels + [
        FieldPanel("events_description"),
    ]
class EventsPage(Page):
    """Main Events Page"""
    template = "home/events_page.html"
    intro_text = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("intro_text"),
        InlinePanel("event_items", label="Event Items"),
    ]


class EventItem(models.Model):
    """Repeatable event items shown on the EventsPage"""
    page = ParentalKey(EventsPage, on_delete=models.CASCADE, related_name="event_items")
    title = models.CharField(max_length=200)
    date = models.DateField()
    description = RichTextField()
    image = models.ForeignKey(
        Image,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+"
    )

    panels = [
        FieldPanel("title"),
        FieldPanel("date"),
        FieldPanel("description"),

    ]

    def __str__(self):
        return self.title

class BlogPage(Page):
    """Blog Page"""
    template = "home/blog_page.html"
    blog_intro = RichTextField()

    content_panels = Page.content_panels + [
        FieldPanel("blog_intro"),
    ]


class ContactPage(Page):
    """Contact Page"""
    template = "home/contact_page.html"
    contact_info = RichTextField()

    content_panels = Page.content_panels + [
        FieldPanel("contact_info"),
    ]


class DonatePage(Page):
    """Donate Now Page"""
    template = "home/donate_now_page.html"
    donation_info = RichTextField()

    content_panels = Page.content_panels + [
        FieldPanel("donation_info"),
    ]
