from datetime import timedelta

from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views import View
from django import forms

from crypto.models import CryptoModel, RuleSet
from crypto.utilities import get_mh_change, get_mh_from_past


def get_cryptos_data():
    """
    This is not a view. It is used in cryptobot.views
    """
    def get_mh_change_with_colors(crypto, **kwargs):
        _mh_change = get_mh_change(crypto, **kwargs)

        if _mh_change > 0.0:
            color = 'success'
        elif _mh_change < 0.0:
            color = 'danger'
        else:
            color = 'dark'

        return '<p class="text-{color}">{change}%</p>'.format(
            color=color, change=_mh_change
        )

    cryptos = CryptoModel.objects.all()
    return_dict = {
        'cryptos': [
            {
                'name': crypto.long_name,
                'price': getattr(get_mh_from_past(crypto), 'price', None),
                'one_hour': get_mh_change_with_colors(crypto, hours=1),
                'twenty_four_hours': get_mh_change_with_colors(crypto, hours=24),
                'three_days': get_mh_change_with_colors(crypto, days=3),
                'seven_days': get_mh_change_with_colors(crypto, days=7),
                'thirty_days': get_mh_change_with_colors(crypto, days=30),
            } for crypto in cryptos],
    }

    return return_dict


def get_crypto_history(request, crypto):
    pass

class RulesetsView(View):
    template_name = "crypto/rulesets.html"

    def get(self, request, crypto):
        if not self.request.user.is_authenticated:
            return HttpResponseRedirect(reverse('registration:login'))

        rs = RuleSet.objects.filter(
            crypto__long_name=crypto.capitalize(),
            owner=self.request.user
        ).order_by('name')

        response_data = {'rulesets': rs, 'crypto': crypto}
        return render(request, self.template_name, response_data)


class AddEditRulesetView(View):
    template_name = "crypto/add_edit_ruleset.html"

    class EditForm(forms.Form):
        name = forms.CharField(max_length=128)
        rtype = forms.ChoiceField(
            choices=(
                ('email', 'email'),
                ('buy', 'buy'),
                ('sell', 'sell')
            )
        )

    def get(self, request, crypto, ruleset_id):
        if not self.request.user.is_authenticated:
            return HttpResponseRedirect(reverse('registration:login'))

        response_data = {
            'header': 'Create new ruleset',
            'crypto': crypto,
            # mock
            'ruleset': {
                'name': '',
                'id': 0,
                'type_of_ruleset': ''
            }
        }

        if ruleset_id:
            try:
                rs = RuleSet.objects.get(
                    id=ruleset_id,
                    crypto=crypto.capitalize(),
                    owner=self.request.user
                ).order_by('name')
            # TODO: add DoesNotExist to pyling pls
            except RuleSet.DoesNotExist:
                pass
            else:
                response_data['header'] = 'Edit'
                response_data['ruleset'] = rs

        return render(request, self.template_name, response_data)

    def post(self, request, crypto, ruleset_id):
        if not self.request.user.is_authenticated:
            return HttpResponseRedirect(reverse('registration:login'))

        form = self.EditForm(request.POST)
        if form.is_valid():
            # TODO: handle adding data
            return HttpResponseRedirect(reverse('crypto:rulesets', args=[crypto]))

        return render(request, self.template_name)
