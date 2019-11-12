from django import forms
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.template.context_processors import csrf
from django.urls import reverse

from registration import models


class CryptoUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Email")

    class Meta:
        model = models.User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super(CryptoUserCreationForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user


def register(request):
    token = {}
    if request.method == "POST":
        form = CryptoUserCreationForm(request.POST)
        if form.is_valid():
            form.save()

            new_user = authenticate(
                username=form.cleaned_data["username"],
                password=form.cleaned_data["password1"],
                email=form.cleaned_data["email"],
            )

            login(request, new_user)
            return HttpResponseRedirect(reverse("registration:registration_complete"))
        else:
            token[
                "error"
            ] = "Error! Password must contain number, special character and length should be at least 8 chars."
    elif request.method == "GET":
        form = CryptoUserCreationForm()
    else:
        form = None

    token.update(csrf(request))
    token["form"] = form
    return render(request, "registration/registration_form.html", token)


def registration_complete(request):
    return render(request, "registration/registration_complete.html")


def loggedin(request):
    return render(
        request, "registration/loggedin.html", {"username": request.user.username}
    )
