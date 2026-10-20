# Allen Family Accounting

Single-page site for Allen Family Accounting: Django 6.1, Tailwind CSS v4 (via
[django-tailwind-cli](https://github.com/django-commons/django-tailwind-cli)),
run in Docker and deployed to Railway. There's no database yet.

The content was ported from the Lovable/Next.js site in
`~/code/allen-family-accounting-site`.

## Layout

- `templates/home.html` – the page, built from `templates/partials/*`
- `templates/icons/` – Lucide icons as SVG includes (`{% include "icons/mail.svg" with cls="w-5 h-5" %}`)
- `assets/css/source.css` – Tailwind source and the site's colour tokens
- `site_pages/views.py` – the page, the services list and the contact form handler
- `public/` – served from the site root (`/favicon.ico`, `/robots.txt`)

The testimonials section is commented out in `templates/home.html` because its
copy is placeholder text. Replace `TESTIMONIALS` in `site_pages/views.py` with
real ones, then remove the `{% comment %}` around the include.

## Local development

```sh
cp .env.example .env   # optional
docker compose up --build
```

Open http://localhost:8000 (if 8000 is taken, `WEB_PORT=8001 docker compose up`). Tailwind rebuilds as templates change. Contact form
emails are printed in the compose log unless `RESEND_API_KEY` or `EMAIL_HOST` is set.

Tests:

```sh
docker compose run --rm web pytest
```

## Deploying to Railway

Railway builds the `Dockerfile` (see `railway.json`), which compiles the CSS and
collects static files; WhiteNoise serves them. The healthcheck is `/up`.

Service variables:

| Variable | Notes |
| --- | --- |
| `SECRET_KEY` | Required. `python -c "import secrets; print(secrets.token_urlsafe(50))"` |
| `RESEND_API_KEY` | Sends contact form emails through [Resend](https://resend.com)'s HTTP API (via [django-anymail](https://anymail.dev)). See below. |
| `CONTACT_EMAIL` | Where enquiries go. Defaults to allenfamilybooks5@gmail.com. |
| `DEFAULT_FROM_EMAIL` | The sender. With Resend, an address on a verified domain; defaults to `onboarding@resend.dev`. With SMTP, defaults to `EMAIL_HOST_USER`. |
| `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `EMAIL_USE_TLS` | SMTP instead of Resend (ignored if `RESEND_API_KEY` is set). Only works on Railway's Pro plan. For Gmail: `smtp.gmail.com`, `587`, the account address and an [app password](https://myaccount.google.com/apppasswords). |
| `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS` | Only for a custom domain, e.g. `allenfamilyaccounting.co.uk` and `https://allenfamilyaccounting.co.uk`. The Railway domain is added automatically. |

### Contact form email (Resend)

Railway blocks outbound SMTP below the Pro plan, so the contact form sends
through Resend's HTTP API instead.

1. Create a Resend account and an API key with "Sending access", and set it as
   `RESEND_API_KEY`.
2. Until a domain is verified, mail comes from `onboarding@resend.dev` and
   Resend only delivers it to the address the account was created with, so
   sign up with `CONTACT_EMAIL` (allenfamilybooks5@gmail.com).
3. Once the site's domain is live, add it under Domains in Resend, create the
   DNS records it lists, and set `DEFAULT_FROM_EMAIL` to e.g.
   `Allen Family Accounting <website@allenfamilyaccounting.co.uk>`.

Enquiries are sent with the visitor's address as Reply-To, so replying in the
inbox answers them directly.
