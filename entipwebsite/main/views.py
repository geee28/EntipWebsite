from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect


# Create your views here.
from . forms import EnterMovies


def home(response):
    return render(response, "main/home.html", {})


def movies(response):
    if response.method == 'POST':
        form = EnterMovies(response.POST)
        if form.is_valid():
            user_movie_name = form.cleaned_data['movieName']
            print("Movie name:", user_movie_name)
            # single_movie_recommendation(user_movie_name, 20, 'single')
            return HttpResponseRedirect('/movies/')
    else:
        form = EnterMovies()
        print("Invalid form")

    return render(response, "main/movies.html", {"form": form})

