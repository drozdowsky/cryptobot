from datetime import timedelta
import logging

from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views import View
from django import forms

from crypto.models import CryptoModel, RuleSet, Rule, Trade, MarketHistoric
from crypto.utilities import (
    get_mh_change,
    get_mh_from_past,
    get_sh_from_past,
    get_data_for_crypto,
)
from crypto.tasks.market_watcher import MarketWatcherParser
from crypto.tasks.social_watcher import SocialWatcherParser

LOGGER = logging.getLogger("crypto.views")


class CryptoView(View):
    template_name = "crypto/cryptos.html"

    def get(self, request):
        if not self.request.user.is_authenticated:
            return HttpResponseRedirect(reverse("registration:login"))

        order_by = request.GET.get("order_by", "long_name")
        cryptos = CryptoModel.objects.all().order_by(order_by)
        data = {
            "cryptos": [],
            "error": "",
        }
        min_date = None

        for crypto in cryptos:
            mh, sh = get_mh_from_past(crypto), get_sh_from_past(crypto)
            market_value, social_value = None, None
            if mh:
                market_value = MarketWatcherParser(
                    mh, LOGGER
                ).get_market_bot_multiplier()
            if sh:
                social_value = SocialWatcherParser(
                    sh, LOGGER
                ).get_social_bot_multiplier()

            chart_data = get_data_for_crypto(crypto)

            date = getattr(mh, "date", 0)
            if min_date:
                min_date = min(min_date, date)
            else:
                min_date = date

            data["cryptos"].append(
                {
                    "name": crypto.long_name,
                    "price": getattr(mh, "price", None),
                    "one_hour": self._get_mh_change_with_colors(crypto, hours=1),
                    "twenty_four_hours": self._get_mh_change_with_colors(
                        crypto, hours=24
                    ),
                    "three_days": self._get_mh_change_with_colors(crypto, days=3),
                    "seven_days": self._get_mh_change_with_colors(crypto, days=7),
                    "thirty_days": self._get_mh_change_with_colors(crypto, days=30),
                    "market_watcher": self._get_color_by_bound(
                        market_value,
                        bound=1.0,
                        # FIXME: don't.
                        format_text='<p title="MarketBot Value from 0.0 to 2.0." class="text-{color}">{value:.2f}</p>',
                    ),
                    "social_watcher": self._get_color_by_bound(
                        social_value,
                        bound=1.0,
                        # FIXME: don't.
                        format_text='<p title="SocialBot Value from 0.0 to 2.0." class="text-{color}">{value:.2f}</p>',
                    ),
                    "data": chart_data,
                }
            )
            data["date"] = min_date

        return render(request, self.template_name, data)

    def _get_mh_change_with_colors(self, crypto, **kwargs):
        mh_change = get_mh_change(crypto, **kwargs)
        return self._get_color_by_bound(mh_change)

    def _get_color_by_bound(self, value, bound=0.0, format_text=""):
        if not value:
            value = 0.0

        if value > bound:
            color = "success"
        elif value < bound:
            color = "danger"
        else:
            color = "dark"

        return (format_text or '<p class="text-{color}">{value:+.2f}%</p>').format(
            color=color, value=value
        )


class RulesetsView(View):
    template_name = "crypto/rulesets.html"

    def get(self, request, crypto, **kwargs):
        if not self.request.user.is_authenticated:
            return HttpResponseRedirect(reverse("registration:login"))

        rs = RuleSet.objects.filter(
            crypto__long_name=crypto.capitalize(), owner=self.request.user
        ).order_by("name")

        response_data = {
            "rulesets": rs,
            "crypto": crypto,
            "error": kwargs.get("error", ""),
        }
        return render(request, self.template_name, response_data)


class AddEditRulesetView(View):
    template_name = "crypto/add_edit_ruleset.html"

    class EditForm(forms.Form):
        name = forms.CharField(max_length=128)
        rtype = forms.ChoiceField(
            choices=(("email", "email"), ("buy", "buy"), ("sell", "sell"))
        )

    def get(self, request, crypto, ruleset_id, **kwargs):
        if not self.request.user.is_authenticated:
            return HttpResponseRedirect(reverse("registration:login"))

        response_data = {
            "header": "Create new ruleset",
            "crypto": crypto,
            # mock
            "ruleset": {"name": "", "id": 0, "type_of_ruleset": ""},
            "ctype": "new",
            "error": kwargs.get("error", ""),
        }

        if ruleset_id:
            try:
                rs = RuleSet.objects.get(
                    id=ruleset_id,
                    crypto__long_name=crypto.capitalize(),
                    owner=self.request.user,
                )
            # TODO: add DoesNotExist to pyling pls
            except RuleSet.DoesNotExist:
                pass
            else:
                response_data["header"] = "Edit"
                response_data["ruleset"] = rs
                response_data["ctype"] = "edit"

        return render(request, self.template_name, response_data)

    def post(self, request, crypto, ruleset_id):
        if not self.request.user.is_authenticated:
            return HttpResponseRedirect(reverse("registration:login"))

        form = self.EditForm(request.POST)
        if form.is_valid():
            crypto = CryptoModel.objects.get(long_name=crypto.capitalize())
            form_name = form.cleaned_data["name"]
            form_rtype = form.cleaned_data["rtype"].capitalize()[0]

            if ruleset_id:
                try:
                    rs = RuleSet.objects.get(
                        id=ruleset_id, owner=self.request.user, crypto=crypto
                    )
                    rs.name = form_name
                    rs.type_of_ruleset = form_rtype
                    rs.save()
                except Exception as e:
                    print(e)
            else:
                try:
                    RuleSet.objects.create(
                        name=form_name,
                        owner=self.request.user,
                        crypto=crypto,
                        type_of_ruleset=form_rtype,
                    )
                except Exception as e:
                    print(e)

        return HttpResponseRedirect(reverse("crypto:rulesets", args=[crypto.long_name]))


class RemoveRulesetView(View):
    template_name = "crypto/remove_ruleset.html"

    def get(self, request, crypto, ruleset_id, **kwargs):
        if not self.request.user.is_authenticated:
            return HttpResponseRedirect(reverse("registration:login"))

        response_data = {
            "header": "Remove",
            "crypto": crypto,
            # mock
            "ruleset": {"name": "", "id": 0},
            "error": kwargs.get("error", ""),
        }

        try:
            rs = RuleSet.objects.get(
                id=ruleset_id,
                crypto__long_name=crypto.capitalize(),
                owner=self.request.user,
            )
        # TODO: add DoesNotExist to pylint pls
        except RuleSet.DoesNotExist:
            return HttpResponseRedirect(
                reverse("crypto:rulesets", args=[crypto.long_name])
            )
        else:
            response_data["ruleset"]["name"] = rs.name
            response_data["ruleset"]["id"] = rs.id

        return render(request, self.template_name, response_data)

    def post(self, request, crypto, ruleset_id):
        if not self.request.user.is_authenticated:
            return HttpResponseRedirect(reverse("registration:login"))

        try:
            rs = RuleSet.objects.get(
                id=ruleset_id, owner=self.request.user, crypto__long_name=crypto
            ).delete()
        except RuleSet.DoesNotExist:
            pass

        return HttpResponseRedirect(reverse("crypto:rulesets", args=[crypto]))


class RulesView(View):
    template_name = "crypto/rules.html"

    def get(self, request, crypto, ruleset_id, **kwargs):
        if not self.request.user.is_authenticated:
            return HttpResponseRedirect(reverse("registration:login"))

        rules = Rule.objects.filter(
            rule_set__crypto__long_name=crypto.capitalize(),
            rule_set__owner=self.request.user,
            rule_set_id=ruleset_id,
        ).order_by("id")

        response_data = {
            "rules": rules,
            "crypto": crypto,
            "ruleset": RuleSet.objects.get(id=ruleset_id, owner=self.request.user),
            "rule_types": {sc: desc for sc, desc in Rule.RULE_DESC},
            "error": kwargs.get("error", ""),
        }
        return render(request, self.template_name, response_data)


class AddEditRuleView(View):
    template_name = "crypto/add_edit_rule.html"

    class EditForm(forms.Form):
        rtype = forms.ChoiceField(choices=Rule.RULE_TYPES)
        value = forms.FloatField()

    def get(self, request, crypto, ruleset_id, rule_id, **kwargs):
        if not self.request.user.is_authenticated:
            return HttpResponseRedirect(reverse("registration:login"))

        ruleset = RuleSet.objects.get(id=ruleset_id, owner=self.request.user)
        response_data = {
            # mock
            "header": "Create new rule",
            "crypto": crypto,
            "rule": {"id": 0, "type_of_rule": "", "value": ""},
            "ruleset": ruleset,
            "rule_types": Rule.RULE_DESC,
            "ctype": "new",
            "error": kwargs.get("error", ""),
        }

        if rule_id:
            try:
                rule = Rule.objects.get(id=rule_id, rule_set=ruleset,)
            except Rule.DoesNotExist:
                pass
            else:
                response_data["header"] = "Edit rule"
                response_data["rule"] = rule
                response_data["ctype"] = "edit"

        return render(request, self.template_name, response_data)

    def post(self, request, crypto, ruleset_id, rule_id):
        if not self.request.user.is_authenticated:
            return HttpResponseRedirect(reverse("registration:login"))

        form = self.EditForm(request.POST)
        if form.is_valid():
            form_rule_type = form.cleaned_data["rtype"]
            form_value = form.cleaned_data["value"]

            if rule_id:
                try:
                    rule = Rule.objects.get(
                        id=rule_id,
                        rule_set_id=ruleset_id,
                        rule_set__owner=self.request.user,
                    )
                    rule.type_of_rule = form_rule_type
                    rule.value = form_value
                    rule.save()
                except Exception as e:
                    print(e)
            else:
                try:
                    if RuleSet.objects.filter(
                        id=ruleset_id, owner=self.request.user
                    ).exists():
                        Rule.objects.create(
                            type_of_rule=form_rule_type,
                            value=form_value,
                            rule_set_id=ruleset_id,
                        )
                except Exception as e:
                    print(e)
        else:
            return self.get(
                request,
                crypto,
                ruleset_id,
                rule_id,
                error="Value must be a real number.",
            )

        return HttpResponseRedirect(reverse("crypto:rules", args=[crypto, ruleset_id]))


class RemoveRuleView(View):
    template_name = "crypto/remove_rule.html"

    def get(self, request, crypto, ruleset_id, rule_id, **kwargs):
        if not self.request.user.is_authenticated:
            return HttpResponseRedirect(reverse("registration:login"))

        response_data = {
            "header": "Remove",
            "crypto": crypto.capitalize(),
            "rule": {"name": "", "id": 0,},
            "ruleset": {"id": ruleset_id,},
            "error": kwargs.get("error", ""),
        }

        try:
            rule = Rule.objects.get(
                id=rule_id, rule_set_id=ruleset_id, rule_set__owner=self.request.user
            )
        except Rule.DoesNotExist:
            return HttpResponseRedirect(
                reverse("crypto:rules", args=[crypto, ruleset_id])
            )
        else:
            response_data["rule"]["name"] = Rule.RULE_DESC_DICT[rule.type_of_rule]
            response_data["rule"]["short_name"] = rule.type_of_rule
            response_data["rule"]["id"] = rule.id
            response_data["ruleset"]["name"] = rule.rule_set.name

        return render(request, self.template_name, response_data)

    def post(self, request, crypto, ruleset_id, rule_id):
        if not self.request.user.is_authenticated:
            return HttpResponseRedirect(reverse("registration:login"))

        try:
            Rule.objects.get(
                id=rule_id, rule_set_id=ruleset_id, rule_set__owner=self.request.user,
            ).delete()
        except Rule.DoesNotExist:
            pass

        return HttpResponseRedirect(reverse("crypto:rules", args=[crypto, ruleset_id]))


class ExecutionLogView(View):
    template_name = "crypto/execution_log.html"

    def get(self, request, crypto, ruleset_id, **kwargs):
        if not self.request.user.is_authenticated:
            return HttpResponseRedirect(reverse("registration:login"))

        try:
            crypto = CryptoModel.objects.get(long_name=crypto.capitalize())
            ruleset = RuleSet.objects.get(id=ruleset_id, owner=self.request.user)
        except (RuleSet.DoesNotExist, CryptoModel.DoesNotExist):
            return HttpResponseRedirect(reverse("crypto:main"))
        else:
            order_by = request.GET.get("order_by", "-date")
            trades = Trade.objects.filter(rule_set=ruleset).order_by(order_by)

        response_data = {
            # mock
            "header": "Execution log for",
            "crypto": crypto,
            "ruleset": ruleset,
            "trades": trades,
            "error": kwargs.get("error", ""),
        }

        return render(request, self.template_name, response_data)


class HistoryView(View):
    template_name = "crypto/history.html"

    def get(self, request, crypto, page, **kwargs):
        if not self.request.user.is_authenticated:
            return HttpResponseRedirect(reverse("registration:login"))

        if page <= 0:
            return HttpResponseRedirect(reverse("crypto:main"))

        order_by = request.GET.get("order_by", "-date")
        q_mh = MarketHistoric.objects.filter(
            crypto__long_name=crypto.capitalize()
        ).order_by(order_by)[(page - 1) * 11 : page * 11]

        response_data = {
            # mock
            "header": "Execution log for",
            "crypto": crypto,
            "historic": q_mh,
            "error": kwargs.get("error", ""),
            "page": page,
        }

        return render(request, self.template_name, response_data)
