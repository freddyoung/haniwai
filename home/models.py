from django.db import models
from django.apps import apps
from django.core.paginator import Paginator
from django.shortcuts import render
from wagtail.models import Page, Orderable
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, InlinePanel
from wagtail.fields import RichTextField
from wagtail.contrib.forms.models import AbstractEmailForm, AbstractFormField
from wagtail.images.models import Image
from wagtail.snippets.models import register_snippet
from modelcluster.fields import ParentalKey
import requests

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

    content_panels = Page.content_panels + [
        FieldPanel("welcome_text"),
        MultiFieldPanel([
            FieldPanel("seo_title"),
            FieldPanel("search_description"),
            FieldPanel("og_image"),
            FieldPanel("no_index"),
        ], heading="SEO Settings"),
    ]

    def get_context(self, request):
        context = super().get_context(request)
        # News/Events Logic
        EventDetailPage = apps.get_model("home", "EventDetailPage")
        try:
            context["news_posts"] = EventDetailPage.objects.live().order_by('-date')[:3]
        except LookupError:
            context["news_posts"] = []
        
        # Programs Logic
        context['programs'] = self.get_children().live().public()

        # Latest Resource
        try:
            ResourcePage = apps.get_model("home", "ResourcePage")
            context["latest_resource"] = ResourcePage.objects.live().order_by('-date').first()
        except LookupError:
            context["latest_resource"] = None

        return context
    
    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        
        # This gives the HTML the "Missions" it needs for the Alpine.js modal
        # Without this, hero.html may be looking for variables that don't exist
        context['missions'] = [
            {
                'id': 'women',
                'title': 'Women Empowerment',
                'iconImg': '/static/images/women-icon.png', # Ensure these exist!
                'description': 'Supporting indigenous women through advocacy and leadership.'
            },
            {
                'id': 'nature',
                'title': 'Nature Protection',
                'iconImg': '/static/images/nature-icon.png',
                'description': 'Protecting our forests and traditional lands.'
            }
        ]
        
        # Ensure News and Resources don't crash the other sections
        context['news_items'] = apps.get_model('home', 'NewsPage').objects.live().order_by('-date')[:3]
        context['resources'] = apps.get_model('home', 'ResourcePage').objects.live().order_by('-date')[:3]
        
        return context
    
# home/models.py

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        
        # Use 'first_published_at' instead of 'date'
        context['news_items'] = EventsPage.objects.live().order_by('-first_published_at')[:3]
        
        # Do the same for resources if they don't have a custom 'date' field
        context['resources'] = ResourcePage.objects.live().order_by('-first_published_at')[:3]
        
        return context
    

    





# =======================
# ABOUT PAGE (Refactored for Lovable Design)
# =======================
# Optional: Simplified AboutPage Model for Hardcoded content
class AboutPage(SeoMixin, Page):
    template = "home/about_page.html"
    
    # We keep the SEO Mixin so you can still edit the Meta Title/Desc in Wagtail
    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel("seo_title"),
            FieldPanel("search_description"),
            FieldPanel("og_image"),
            FieldPanel("no_index"),
        ], heading="SEO Settings"),
    ]


# =======================
# OTHER PAGES (Standard)
# =======================

class FAQPage(SeoMixin, Page):
    # Change 'faq_page.html' to 'faqs_page.html' to match your file name
    template = "home/faqs_page.html" 

    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel("seo_title"),
            FieldPanel("search_description"),
            FieldPanel("og_image"),
            FieldPanel("no_index"),
        ], heading="SEO Settings"),
    ]

class ProgramsPage(SeoMixin, Page):
    template = "home/programs_page.html"

    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel("seo_title"),
            FieldPanel("search_description"),
            FieldPanel("og_image"),
            FieldPanel("no_index"),
        ], heading="SEO Settings"),
    ]

class EventsPage(SeoMixin, Page):
    template = "home/events_page.html"
    intro_text = RichTextField(blank=True)
    content_panels = Page.content_panels + [FieldPanel("intro_text"), MultiFieldPanel([FieldPanel("seo_title"), FieldPanel("search_description"), FieldPanel("og_image")], heading="SEO Settings")]

class EventDetailPage(SeoMixin, Page):
    CONTENT_TYPE_CHOICES = [('news', 'News'), ('event', 'Event')]
    category = models.CharField(max_length=10, choices=CONTENT_TYPE_CHOICES, default='news')
    date = models.DateField("Event Date")
    intro = models.CharField(max_length=250)
    body = RichTextField()
    image = models.ForeignKey('wagtailimages.Image', null=True, blank=True, on_delete=models.SET_NULL, related_name='+')
    content_panels = Page.content_panels + [FieldPanel("category"), FieldPanel("date"), FieldPanel("intro"), FieldPanel("body"), FieldPanel("image"), MultiFieldPanel([FieldPanel("seo_title"), FieldPanel("search_description"), FieldPanel("og_image")], heading="SEO Settings")]

class ContactFormField(AbstractFormField):
    page = ParentalKey('ContactPage', on_delete=models.CASCADE, related_name='form_fields')

class ContactPage(SeoMixin, AbstractEmailForm):
    template = "home/contact_page.html"
    landing_page_template = "home/contact_landing_page.html" 

    intro = RichTextField(blank=True)
    hotline_number = models.CharField(max_length=100, default="(+675) 7206 7138")
    office_address = models.TextField(default="Allotment 74, Section 193, Atlas Street, Hohola, NCD, PNG")

    content_panels = AbstractEmailForm.content_panels + [
        FieldPanel('intro'),
        MultiFieldPanel([
            FieldPanel('hotline_number'),
            FieldPanel('office_address'),
        ], heading="Contact Information"),
        InlinePanel('form_fields', label="Form fields"),
        MultiFieldPanel([
            FieldPanel('from_address'),
            FieldPanel('to_address'),
            FieldPanel('subject'),
        ], heading="Email Configuration"),
    ]

    def serve(self, request, *args, **kwargs):
        if request.method == 'POST':
            # --- SECURITY CHECK 1: HONEYPOT ---
            # If the hidden field 'website_url' is filled, it's a bot.
            if request.POST.get('website_url'):
                # Fail silently: Render the page as if nothing happened (fresh form)
                form = self.get_form(page=self, user=request.user)
                return render(request, self.get_template(request), {'page': self, 'form': form})

            # --- SECURITY CHECK 2: CLOUDFLARE TURNSTILE ---
            turnstile_token = request.POST.get('cf-turnstile-response')
            secret_key = "0x4AAAAAACaybPNCx7778lKJ5ceiCwABVS0"  # <--- PASTE KEY HERE
            
            try:
                verify = requests.post(
                    'https://challenges.cloudflare.com/turnstile/v0/siteverify',
                    data={
                        'secret': secret_key,
                        'response': turnstile_token,
                        'remoteip': request.META.get('REMOTE_ADDR')
                    },
                    timeout=5
                )
                result = verify.json()
            except requests.RequestException:
                # If connection to Cloudflare fails, we log it and default to blocking
                # or you can set result = {'success': True} to fail open.
                result = {'success': False}

            if not result.get('success'):
                # If check fails, reload page with an error
                form = self.get_form(request.POST, request.FILES, page=self, user=request.user)
                form.add_error(None, "Security check failed. Please refresh and try again.")
                return render(request, self.get_template(request), {'page': self, 'form': form})

            # --- EXISTING SUCCESS LOGIC ---
            form = self.get_form(request.POST, request.FILES, page=self, user=request.user)

            if form.is_valid():
                self.process_form_submission(form)
                
                # Render the same page but pass 'submitted=True' to the context
                return render(request, self.get_template(request), {
                    'page': self,
                    'form': form,
                    'submitted': True,
                })
        else:
            form = self.get_form(page=self, user=request.user)

        return render(request, self.get_template(request), {
            'page': self,
            'form': form,
        })


class DonatePage(SeoMixin, Page):
    # Updated to match your filename: donation_page.html
    template = "home/donation_page.html" 
    
    donation_info = RichTextField()
    content_panels = Page.content_panels + [
        FieldPanel("donation_info"), 
        MultiFieldPanel([
            FieldPanel("seo_title"), 
            FieldPanel("search_description"), 
            FieldPanel("og_image")
        ], heading="SEO Settings")
    ]

class ResourcesIndexPage(SeoMixin, Page):
    template = 'home/resources_page.html'
    intro = RichTextField(blank=True)
    content_panels = Page.content_panels + [FieldPanel('intro'), MultiFieldPanel([FieldPanel('seo_title'), FieldPanel('search_description'), FieldPanel('og_image')], heading='SEO Settings')]
    subpage_types = ['ResourcePage']
    
    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        all_resources = ResourcePage.objects.live().descendant_of(self).order_by('-date')
        paginator = Paginator(all_resources, 6)
        page_obj = paginator.get_page(request.GET.get('page'))
        context['resources'] = page_obj
        return context

class ResourcePage(SeoMixin, Page):
    template = 'home/resource_detail_page.html'
    date = models.DateField('Publication Date')
    intro = RichTextField(blank=True)
    resource_file = models.ForeignKey('wagtaildocs.Document', null=True, blank=True, on_delete=models.SET_NULL, related_name='+')
    resource_image = models.ForeignKey('wagtailimages.Image', null=True, blank=True, on_delete=models.SET_NULL, related_name='+')
    content_panels = Page.content_panels + [FieldPanel('date'), FieldPanel('intro'), FieldPanel('resource_image'), FieldPanel('resource_file'), MultiFieldPanel([FieldPanel('seo_title'), FieldPanel('search_description'), FieldPanel('og_image')], heading='SEO Settings')]

@register_snippet
class NewsletterSubscriber(models.Model):
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    panels = [FieldPanel('email')]
    def __str__(self): return self.email
    class Meta: verbose_name_plural = "Newsletter Subscribers"