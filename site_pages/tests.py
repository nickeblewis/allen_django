from urllib.parse import unquote

VALID = {"name": "Jane Doe", "email": "jane@example.com", "message": "I need help with my tax return."}


def test_home_renders(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Allen Family" in response.content
    assert b"Bookkeeping" in response.content
    assert b'name="csrfmiddlewaretoken"' in response.content


def test_testimonials_are_hidden_until_real_ones_exist(client):
    assert b"What Our Clients Say" not in client.get("/").content


def test_whatsapp_link(client):
    content = client.get("/").content
    assert b"https://wa.me/447717453767?text=" in content
    assert b"+44 7717 453767" in content


def test_up(client):
    response = client.get("/up")
    assert response.status_code == 200
    assert response.content == b"ok"


def test_contact_form_opens_whatsapp(client, settings):
    settings.WHATSAPP_NUMBERS = ["447700900123"]
    response = client.post("/", VALID)
    assert response.status_code == 302
    location = unquote(response["Location"])
    assert location.startswith("https://wa.me/447700900123?text=")
    assert "Jane Doe (jane@example.com)" in location
    assert "tax return" in location


def test_contact_form_shows_errors(client):
    response = client.post("/", {**VALID, "email": "not-an-email"})
    assert response.status_code == 200
    assert b"Enter a valid email address." in response.content


def test_honeypot_drops_submission_quietly(client):
    response = client.post("/", {**VALID, "website": "http://spam.example"})
    assert response.status_code == 302
    assert response["Location"] == "/#contact"


def test_404_page(client, settings):
    settings.DEBUG = False
    response = client.get("/no-such-page")
    assert response.status_code == 404
    assert b"Page not found" in response.content
