from django.db import models
from wagtail.models import Page
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, InlinePanel, PageChooserPanel
from wagtail.fields import RichTextField
from wagtail.images.models import Image
from modelcluster.fields import ParentalKey
from django.core.paginator import Paginator
from django.db.models import Q
from django.apps import apps
from django.utils.html import strip_tags
from django.utils.text import Truncator

from wagtail import blocks
from wagtail.documents.models import Document


# =======================
# SEO Mixin
# =======================

class SeoMixin(models.Model):
    og_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text="Image used when sharing this page on social media."
    )
    no_index = models.BooleanField(
        default=False,
        help_text="Prevent search engines from indexing this page."
    )

    class Meta:
        abstract = True

    def get_seo_title(self):
        return self.seo_title or self.title

    def get_seo_description(self):
        return self.search_description or ""

    def get_og_image_url(self):
        return self.og_image.file.url if self.og_image else None



# =======================
# HOME PAGE
# =======================

class HomePage(SeoMixin, Page):
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
        MultiFieldPanel([
            FieldPanel("seo_title"),
            FieldPanel("search_description"),
            FieldPanel("og_image"),
            FieldPanel("no_index"),
        ], heading="SEO Settings"),
    ]

    def get_context(self, request):
        context = super().get_context(request)
        images = self.gallery_images.all().order_by('id')
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

        EventDetailPage = apps.get_model("home", "EventDetailPage")
        context["latest_news"] = EventDetailPage.objects.live().order_by('-date')[:3]

        # Add the latest resource to the context
        context["latest_resource"] = ResourcePage.objects.live().order_by('-date').first()

        return context

    def get_structured_data(self):
        """Injects event data only for EventDetailPage. Extendable."""
        if hasattr(self, 'date'):
            return {
                "@context": "https://schema.org",
                "@type": "Event",
                "name": self.title,
                "startDate": self.date.isoformat(),
                "description": self.search_description or self.intro,
                "url": self.full_url,
                "image": self.get_og_image_url(),
                "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
                "eventStatus": "https://schema.org/EventScheduled",
                "location": {
                    "@type": "Place",
                    "name": "Papua New Guinea",
                    "address": {
                        "@type": "PostalAddress",
                        "addressCountry": "PG"
                    }
                }
            }
        return None


class GalleryImage(models.Model):
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

class GalleryPage(SeoMixin, Page):
    template = "home/gallery_page.html"
    description = RichTextField(blank=True, null=True)

    content_panels = Page.content_panels + [
        FieldPanel("description"),
        MultiFieldPanel([
            FieldPanel("seo_title"),
            FieldPanel("search_description"),
            FieldPanel("og_image"),
        ], heading="SEO Settings"),
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

class AboutPage(SeoMixin, Page):
    template = "home/about_page.html"
    description = RichTextField()

    content_panels = Page.content_panels + [
        FieldPanel("description"),
        MultiFieldPanel([
            FieldPanel("seo_title"),
            FieldPanel("search_description"),
            FieldPanel("og_image"),
        ], heading="SEO Settings"),
    ]


# =======================
# EVENTS HUB PAGE
# =======================

class EventsPage(SeoMixin, Page):
    template = "home/events_page.html"
    intro_text = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("intro_text"),
        MultiFieldPanel([
            FieldPanel("seo_title"),
            FieldPanel("search_description"),
            FieldPanel("og_image"),
        ], heading="SEO Settings"),
    ]


# =======================
# EVENT / NEWS DETAIL PAGE
# =======================

class EventDetailPage(SeoMixin, Page):
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
        MultiFieldPanel([
            FieldPanel("seo_title"),
            FieldPanel("search_description"),
            FieldPanel("og_image"),
        ], heading="SEO Settings"),
    ]

    def is_previewable(self):
        return True
    
def get_event_schema(self):
    base_schema = {
        "@context": "https://schema.org",
        "@type": "Event" if self.category == "event" else "NewsArticle",
        "name": self.seo_title or self.title,
        "description": Truncator(strip_tags(self.body)).chars(200),
        "url": self.full_url,
        "image": [self.image.file.url] if self.image else ["https://www.haniwai.org/static/images/social-preview.jpeg"],
        "publisher": {
            "@type": "Organization",
            "name": "HANIWAI",
            "logo": {
                "@type": "ImageObject",
                "url": "https://www.haniwai.org/static/images/haniwa_logo.png"
            }
        }
    }

    # Add Event-specific details if it's an event
    if self.category == "event":
        base_schema.update({
            "startDate": self.date.isoformat(),
            "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
            "eventStatus": "https://schema.org/EventScheduled",
            "location": {
                "@type": "Place",
                "name": "Papua New Guinea",
                "address": {
                    "@type": "PostalAddress",
                    "addressCountry": "PG"
                }
            }
        })

    return base_schema



# =======================
# CONTACT PAGE
# =======================

class ContactPage(SeoMixin, Page):
    template = "home/contact_page.html"
    contact_info = RichTextField()

    content_panels = Page.content_panels + [
        FieldPanel("contact_info"),
        MultiFieldPanel([
            FieldPanel("seo_title"),
            FieldPanel("search_description"),
            FieldPanel("og_image"),
        ], heading="SEO Settings"),
    ]


# =======================
# DONATE PAGE
# =======================

class DonatePage(SeoMixin, Page):
    template = "home/donate_now_page.html"
    donation_info = RichTextField()

    content_panels = Page.content_panels + [
        FieldPanel("donation_info"),
        MultiFieldPanel([
            FieldPanel("seo_title"),
            FieldPanel("search_description"),
            FieldPanel("og_image"),
        ], heading="SEO Settings"),
    ]


# =======================
# RESOURCES PAGE (NEW)
# =======================

class ResourcesIndexPage(SeoMixin, Page):
    template = 'home/resources_page.html'
    intro = RichTextField(blank=True, help_text='Text to describe the resources section.')

    content_panels = Page.content_panels + [
        FieldPanel('intro'),
        MultiFieldPanel([
            FieldPanel('seo_title'),
            FieldPanel('search_description'),
            FieldPanel('og_image'),
        ], heading='SEO Settings'),
    ]

    subpage_types = ['ResourcePage']

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        all_resources = ResourcePage.objects.live().descendant_of(self).order_by('-date')

        # Pagination for resources
        paginator = Paginator(all_resources, 6)  # Adjust per page as needed
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context['resources'] = page_obj
        return context

    class Meta:
        verbose_name = 'Resources Index Page'
        verbose_name_plural = 'Resources Index Pages'


class ResourcePage(SeoMixin, Page):
    template = 'home/resource_detail_page.html'
    date = models.DateField('Publication Date', help_text='Date the resource was published.')
    intro = RichTextField(blank=True, help_text='A short introduction or summary of the resource.')
    resource_file = models.ForeignKey(
        'wagtaildocs.Document',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text='Upload the newsletter or annual report PDF/document.'
    )
    resource_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text='Image to represent the resource (e.g., cover of newsletter).'
    )

    content_panels = Page.content_panels + [
        FieldPanel('date'),
        FieldPanel('intro'),
        FieldPanel('resource_image'),
        FieldPanel('resource_file'),
        MultiFieldPanel([
            FieldPanel('seo_title'),
            FieldPanel('search_description'),
            FieldPanel('og_image'),
        ], heading='SEO Settings'),
    ]

    parent_page_types = ['ResourcesIndexPage']
    
    def get_other_resources(self):
        return ResourcePage.objects.live().sibling_of(self).exclude(id=self.id).order_by('-date')[:5]


    class Meta:
        verbose_name = 'Resource Page'
        verbose_name_plural = 'Resource Pages'