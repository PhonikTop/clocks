# shortener_app/forms.py

from django import forms
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError


class URLShortenerForm(forms.Form):
    url = forms.CharField(
        label='URL',
        max_length=1000,
        widget=forms.URLInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your URL here',
            'required': 'required'
        }),
        validators=[URLValidator(message="Enter a valid URL.")]
    )

    def clean_url(self):
        url = self.cleaned_data.get('url')
        # Perform additional custom validation here if needed
        # For example, you can check if the URL already exists in the database
        return url
