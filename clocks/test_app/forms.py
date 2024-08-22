from django import forms
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError


class URLShortenerForm(forms.Form):
    url = forms.URLField(
        label="",
        max_length=2000,
        widget=forms.URLInput(
            attrs={"placeholder": "Введи URL", "class": "form-control"}
        ),
        error_messages={
            "required": "This field is required",
            "invalid": "Enter a valid URL",
        },
    )
