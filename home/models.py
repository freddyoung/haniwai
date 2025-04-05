from django.db import models
from wagtail.models import Page
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, InlinePanel, PageChooserPanel
from wagtail.fields import RichTextField
from wagtail.images.models import Image
from modelcluster.fields import ParentalKey
from django.core.paginator import Paginator
from django.db.models import Q
from django.apps import apps


# =======================
# HOME PAGE
# =======================

class HomePage(Page):
    """Custom Home Page with gallery and news/events preview."""
    template = "home/home_page.html"
    welcome_text = models.CharField(max_length=255, default="Welcome to Our NGO")

    gallery_page = models.ForeignKey(
        "home.GalleryPage",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+"
    )

    content_panels = Page.content_panels + [
        FieldPanel("welcome_text"),
        PageChooserPanel("gallery_page"),
        MultiFieldPanel([
            InlinePanel("gallery_images", label="Gallery Images"),
        ], heading="Gallery Section"),
    ]

    def get_context(self, request):
        context = super().get_context(request)

        # Gallery filtering & pagination
        images = self.gallery_images.all()
        query = request.GET.get("q")
        if query:
            images = images.filter(
                Q(image__title__icontains=query) |
                Q(image__tags__name__icontains=query) |
                Q(image__description__icontains=query)
            ).distinct()

        paginator = Paginator(images, 20)
        page_number = request.GET.get("page")
        page_obj = paginator.get_page(page_number)

        context["gallery_images"] = page_obj
        context["query"] = query

        # Show 3 latest event/news previews
        EventDetailPage = apps.get_model("home", "EventDetailPage")
        context["latest_news"] = EventDetailPage.objects.live().order_by('-date')[:3]

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


# =======================
# GALLERY PAGE
# =======================

class GalleryPage(Page):
    """Gallery Page - Displays All Images"""
    template = "home/gallery_page.html"
    description = RichTextField(blank=True, null=True)

    content_panels = Page.content_panels + [
        FieldPanel("description"),
    ]

    def get_context(self, request):
        context = super().get_context(request)
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


# =======================
# ABOUT PAGE
# =======================

class AboutPage(Page):
    template = "home/about_page.html"
    description = RichTextField()

    content_panels = Page.content_panels + [
        FieldPanel("description"),
    ]


# =======================
# EVENTS HUB PAGE
# =======================

class EventsPage(Page):
    """Hub page for listing EventDetailPages"""
    template = "home/events_page.html"
    intro_text = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("intro_text"),
    ]


# =======================
# EVENT / NEWS DETAIL PAGE
# =======================

class EventDetailPage(Page):
    """Individual Event or News Article"""

    CONTENT_TYPE_CHOICES = [
        ('news', 'News'),
        ('event', 'Event'),
    ]

    category = models.CharField(
        max_length=10,
        choices=CONTENT_TYPE_CHOICES,
        default='news',
        help_text="Is this a News or Event item?"
    )

    date = models.DateField("Event Date")
    intro = models.CharField(max_length=250, help_text="Short summary for preview cards")
    body = RichTextField()
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    content_panels = Page.content_panels + [
        FieldPanel("category"),
        FieldPanel("date"),
        FieldPanel("intro"),
        FieldPanel("body"),
        FieldPanel("image"),
    ]

    def is_previewable(self):
        return True  # Optional, avoids Wagtail admin preview error



# =======================
# CONTACT PAGE
# =======================

class ContactPage(Page):
    template = "home/contact_page.html"
    contact_info = RichTextField()

    content_panels = Page.content_panels + [
        FieldPanel("contact_info"),
    ]


# =======================
# DONATE PAGE
# =======================

class DonatePage(Page):
    template = "home/donate_now_page.html"
    donation_info = RichTextField()

    content_panels = Page.content_panels + [
        FieldPanel("donation_info"),
    ]
