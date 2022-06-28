from django import forms


class EnterMovies(forms.Form):
    movieName = forms.CharField(label="", max_length=200,
                                widget=forms.TextInput(attrs={'placeholder': 'Enter a movie'}))
