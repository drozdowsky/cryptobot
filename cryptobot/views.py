from django.views import View
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse

from crypto.views import get_cryptos_data


class MainView(View):
    template_name = "crypto/cryptos.html"

    def get(self, request):
        if not self.request.user.is_authenticated:
            return HttpResponseRedirect(reverse('registration:login'))

        return render(request, self.template_name, get_cryptos_data())
