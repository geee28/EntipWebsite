from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
import pandas as pd
import numpy as np
import os
import ast
import nltk
from nltk.stem.porter import PorterStemmer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.corpus import wordnet

nltk.download('wordnet')


def home(response):
    return render(response, "main/home.html", {})


def series(response):
    return render(response, "main/series.html", {})


def songs(response):
    return render(response, "main/songs.html", {})


def movies(response):
    recommended_movies_list = []
    if response.method == 'POST':
        print("inside POST method")
        alldata = response.POST
        print(alldata)
        movienames = alldata.getlist('user_movies[]')
        for movie in movienames:
            if movie == '':
                print("ERROR! NULL MOVIE NOT ALLOWED")

        model_movies_df = pd.read_csv(r"./main/static/main/database/5000_records_movies.csv",
                                      converters={'genres': list, 'overview': list, 'keywords': list, 'cast': list,
                                                  'crew': list})
        if len(movienames) == 1:
            sorted_movie_list = single_movie_recommendation(model_movies_df, movienames[0], 16, 'single')
            for i in sorted_movie_list:
                recommended_movies_list.append(
                    " ".join(model_movies_df[model_movies_df['movie_id'] == i[0]].title.tolist()))
            print(recommended_movies_list)
        else:
            recommended_movies_list = multiple_movie_recommendation(model_movies_df, movienames)
            print(recommended_movies_list)
    else:
        print("refresh")

    return render(response, "main/movies.html", {"recommendedmovieslist": recommended_movies_list})


def single_movie_recommendation(model_movies_df, moviename, headnum, flag):
    if flag == 'multiple':
        model_movies_df['tags'] = model_movies_df['genres'] + model_movies_df['keywords'] + model_movies_df['overview']
    if flag == 'single':
        model_movies_df['tags'] = model_movies_df['overview'] + model_movies_df['genres'] + model_movies_df[
            'keywords'] + model_movies_df['cast'] + model_movies_df['crew']

    df = model_movies_df[['movie_id', 'title', 'tags', 'vote_average', 'popularity']]

    df['tags'] = df['tags'].apply(lambda x: "".join(x))
    df['tags'] = df['tags'].apply(lambda x: x.lower())
    df['tags'] = df['tags'].apply(stem)
    cvobj = CountVectorizer(max_features=6000, stop_words='english')
    vectors = cvobj.fit_transform(df['tags']).toarray()
    similarity = cosine_similarity(vectors)
    movie_index = df[df['title'] == moviename].index[0]
    distances = similarity[movie_index]

    recommendedlist = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:headnum]
    imdbrecommendedlist = []

    for i in recommendedlist:
        i = list(i)
        i.append(df.iloc[i[0]]['vote_average'])
        i[0] = df.iloc[i[0]]['movie_id']
        imdbrecommendedlist.append(i)

    roundimdblist = []
    for i in imdbrecommendedlist:
        roundimdblist.append([i[0], round(i[1], 2), i[2]])
    return sorted(roundimdblist, reverse=True, key=lambda x: (x[1], x[2]))


def synonym(word):
    synonyms = []
    for syn in wordnet.synsets(word):
        for l in syn.lemmas():
            synonyms.append(l.name())
    return synonyms


def stem(text):
    psobj = PorterStemmer()
    temp = []
    for i in text.split():
        temp.append(psobj.stem(i))
    return " ".join(temp)


def functolist(lst):
    return " ".join(lst)


def multiple_movie_recommendation(df, multiplemovielist):
    print("mulitple movie list", multiplemovielist)
    firstlevellist = []
    for i in multiplemovielist:
        firstlevellist.extend(single_movie_recommendation(df, i, 40, 'multiple'))
    movie_id_of_users_input_list = []
    tag_of_users_input_list = []
    for movie in multiplemovielist:
        idofmovie = df[df['title'] == movie]['movie_id'].item()
        movie_id_of_users_input_list.append(idofmovie)
        tag_of_users_input_list.append(stem(" ".join(df[df['movie_id'] == idofmovie]['tags'].item())))
    movie_id_of_firstlevellist_movies = []
    for i in firstlevellist:
        movie_id_of_firstlevellist_movies.append(i[0])
    new_df = df[df['movie_id'].isin(movie_id_of_firstlevellist_movies)]
    new_df['tags'] = new_df['tags'].apply(functolist)
    new_df['tags'] = new_df['tags'].apply(stem)

    counterobjlist = []
    newmovielist = []

    for indicer in range(len(new_df)):
        counters = np.zeros((len(tag_of_users_input_list), 1))
        for i in new_df.iloc[indicer]['tags'].split():
            for j in range(len(tag_of_users_input_list)):
                if (stem(i) in tag_of_users_input_list[j].split()) or (
                        stem(" ".join(synonym(i))) in tag_of_users_input_list[j].split()):
                    counters[j] += 1
        if all(x >= 1 for x in counters):
            newmovielist.append([new_df.iloc[indicer]['title'], new_df.iloc[indicer]['vote_average']])
            counterobjlist.append(counters)
    if len(newmovielist) > 16:
        newmovielist = sorted(newmovielist, reverse=True, key=lambda x: x[1])[:16]
    else:
        newmovielist = sorted(newmovielist, reverse=True, key=lambda x: x[1])
    mylist = []
    for item in newmovielist:
        mylist.append(item[0])
    return mylist