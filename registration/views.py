from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib.auth.forms import UserCreationForm
from django.template.context_processors import csrf
from django.urls import reverse
from django.contrib.auth import authenticate, login, views


def main(request):
    if request.user.is_authenticated():
        return loggedin(request)

    return views.login(request)


def register(request):
    token = {}
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()

            new_user = authenticate(username=form.cleaned_data['username'],
                                    password=form.cleaned_data['password1'],
                                    )

            login(request, new_user)
            return HttpResponseRedirect(reverse('registration:registration_complete'))
        else:
            token['error'] = 'Error! Follow the rules :('
    else:
        form = UserCreationForm()

    token.update(csrf(request))
    token['form'] = form

    return render(request, 'registration/registration_form.html', token)


def registration_complete(request):
    return render(request, 'registration/registration_complete.html')


def loggedin(request):
    return render(request, 'registration/loggedin.html',
                  {'username': request.user.username})





