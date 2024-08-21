from django.shortcuts import render
from .forms import URLShortenerForm
from .redis_client import get_all_urls, save_url_to_redis


def shorten_url(request):
    if request.method == "POST":
        # form = URLShortenerForm(request.POST)
        # if form.is_valid():
        #     print(form.cleaned_data)
        form = URLShortenerForm()
        save_url_to_redis(request.POST.get("url"), url)
    else:
        form = URLShortenerForm()

    return render(request, "index.html",
                  {"form": form, "existing_urls": get_all_urls()})


def redirect_view(request, short_url):
    original_url = get_url_from_redis(short_url)
    if original_url:
        increment_url_stat(short_url)
        return HttpResponseRedirect(original_url)
    else:
        return render(request, '404.html', status=404)
