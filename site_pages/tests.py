from django.core import mail

VALID = {"name": "Jane Doe", "email": "jane@example.com", "message": "I need help with my tax return."}


def test_home_renders(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Allen Family" in response.content
    assert b"Bookkeeping" in response.content
    assert b'name="csrfmiddlewaretoken"' in response.content


def test_testimonials_are_hidden_until_real_ones_exist(client):
    assert b"What Our Clients Say" not in client.get("/").content


def test_up(client):
    response = client.get("/up")
    assert response.status_code == 200
    assert response.content == b"ok"


def test_contact_form_sends_email(client, settings):
    settings.CONTACT_EMAIL = "office@example.com"
    response = client.post("/", VALID)
    assert response.status_code == 302
    assert response["Location"] == "/#contact"
    assert len(mail.outbox) == 1
    sent = mail.outbox[0]
    assert sent.to == ["office@example.com"]
    assert sent.reply_to == ["jane@example.com"]
    assert "Jane Doe" in sent.subject
    assert "tax return" in sent.body

    followed = client.get("/")
    assert b"Message sent!" in followed.content


def test_contact_form_shows_errors(client):
    response = client.post("/", {**VALID, "email": "not-an-email"})
    assert response.status_code == 200
    assert b"Enter a valid email address." in response.content
    assert len(mail.outbox) == 0


def test_honeypot_drops_submission_quietly(client):
    response = client.post("/", {**VALID, "website": "http://spam.example"})
    assert response.status_code == 302
    assert len(mail.outbox) == 0


def test_404_page(client, settings):
    settings.DEBUG = False
    response = client.get("/no-such-page")
    assert response.status_code == 404
    assert b"Page not found" in response.content
