from django import forms

INPUT_CLASSES = (
    "w-full px-4 py-3 rounded-lg border border-input bg-background text-foreground "
    "placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-accent/50 "
    "focus:border-accent transition-colors"
)


class ContactForm(forms.Form):
    name = forms.CharField(
        label="Full Name",
        max_length=200,
        widget=forms.TextInput(attrs={"class": INPUT_CLASSES, "placeholder": "John Smith", "autocomplete": "name"}),
    )
    email = forms.EmailField(
        label="Email Address",
        widget=forms.EmailInput(
            attrs={"class": INPUT_CLASSES, "placeholder": "john@example.com", "autocomplete": "email"}
        ),
    )
    message = forms.CharField(
        label="How can we help?",
        max_length=5000,
        widget=forms.Textarea(
            attrs={
                "class": INPUT_CLASSES + " resize-none",
                "rows": 4,
                "placeholder": "Tell us about your accounting needs...",
            }
        ),
    )
    # Honeypot: hidden from people, filled in by bots.
    website = forms.CharField(required=False)

    def is_spam(self) -> bool:
        return bool(self.cleaned_data.get("website"))
