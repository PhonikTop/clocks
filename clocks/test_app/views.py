from django.shortcuts import render
from .forms import URLShortenerForm


def shorten_url(request):
    if request.method == "POST":
        # form = URLShortenerForm(request.POST)
        # if form.is_valid():
        #     print(form.cleaned_data)
        form = URLShortenerForm()
        url = request.POST.get("url")
        print(url)

    else:
        form = URLShortenerForm()

    return render(request, "index.html",
                  {"form": form, "existing_urls": ["example.com"]})
