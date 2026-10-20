import logging

from django.conf import settings
from django.contrib import messages
from django.core.mail import EmailMessage
from django.http import HttpResponse
from django.shortcuts import redirect, render

from .forms import ContactForm

logger = logging.getLogger(__name__)

SERVICES = [
    {"icon": "file-text", "title": "Bookkeeping",
     "description": "Accurate record-keeping to keep your finances organized year-round."},
    {"icon": "users", "title": "Payroll Services",
     "description": "Reliable payroll processing for businesses of all sizes."},
    {"icon": "building", "title": "VAT Returns",
     "description": "Accurate and timely VAT return preparation and submission."},
]

# Placeholder copy from the Lovable site. The section is commented out in
# templates/home.html until there are real testimonials to show.
TESTIMONIALS = [
    {"name": "Sarah Mitchell", "role": "Small Business Owner", "rating": 5,
     "content": "Allen Family Accounting has been managing our books for over 5 years. "
                "Their attention to detail and personal touch is unmatched."},
    {"name": "James Thompson", "role": "Retired Teacher", "rating": 5,
     "content": "They made my retirement planning so much easier to understand. "
                "I finally feel confident about my financial future."},
    {"name": "Emily Chen", "role": "Restaurant Owner", "rating": 5,
     "content": "Professional, responsive, and truly caring. They treat our business like their own family."},
    {"name": "Robert Williams", "role": "Freelance Consultant", "rating": 5,
     "content": "Best decision I made was switching to Allen Family. "
                "My taxes are done right, on time, every time."},
]


def up(request):
    """Railway's healthcheck. Deliberately touches nothing but the process."""
    return HttpResponse("ok", content_type="text/plain")


def home(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            if form.is_spam():
                logger.info("Dropped contact form submission caught by the honeypot.")
            else:
                data = form.cleaned_data
                email = EmailMessage(
                    subject=f"Website enquiry from {data['name']}",
                    body=f"Name: {data['name']}\nEmail: {data['email']}\n\n{data['message']}",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[settings.CONTACT_EMAIL],
                    reply_to=[data["email"]],
                )
                try:
                    email.send()
                except Exception:
                    logger.exception("Couldn't send contact form email.")
                    messages.error(
                        request,
                        f"Sorry, your message couldn't be sent. Please email us at {settings.CONTACT_EMAIL}.",
                    )
                    return render_home(request, form)
            messages.success(request, "Message sent! We'll get back to you within 24 hours.")
            return redirect("/#contact")
    else:
        form = ContactForm()
    return render_home(request, form)


def render_home(request, form):
    context = {
        "form": form,
        "services": [{**s, "delay": i / 10} for i, s in enumerate(SERVICES)],
        "testimonials": [{**t, "delay": i / 10, "stars": range(t["rating"])} for i, t in enumerate(TESTIMONIALS)],
    }
    return render(request, "home.html", context)
