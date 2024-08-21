# from django.shortcuts import render
#
#
# def shorten_url(request):
#     if request.method == 'GET':
#         if form := request.GET["url"] is not None:
#             return render(request, 'index.html', {'form': form})
#         return render(request, 'index.html')
#     else:
#         form = "Пусто"
#


from django.shortcuts import render
from .forms import URLShortenerForm


def shorten_url(request):
    if request.method == 'POST':
        form = URLShortenerForm(request.POST)
        if form.is_valid():
            print(form.cleaned_data)
    else:
        form = URLShortenerForm()

    return render(request, 'index.html', {
        'form': form,
    })
