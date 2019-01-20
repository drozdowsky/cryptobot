from django.urls import path
from .views import *

app_name = 'crypto'


urlpatterns = [
    path(r'', CryptoView.as_view(), name='main'),
    path(r'history/<str:crypto>/<int:page>/', HistoryView.as_view(), name='history'),
    path(r'rulesets/<str:crypto>/', RulesetsView.as_view(), name='rulesets'),
    path(r'ruleset/add_or_edit/<str:crypto>/<int:ruleset_id>/', AddEditRulesetView.as_view(), name='add_edit_ruleset'),
    path(r'ruleset/remove/<str:crypto>/<int:ruleset_id>/', RemoveRulesetView.as_view(), name='remove_ruleset'),
    path(r'ruleset/execution/<str:crypto>/<int:ruleset_id>/', ExecutionLogView.as_view(), name='execution_log'),
    path(r'rules/<str:crypto>/<int:ruleset_id>/', RulesView.as_view(), name='rules'),
    path(r'rules/add_or_edit/<str:crypto>/<int:ruleset_id>/<int:rule_id>', AddEditRuleView.as_view(), name='add_edit_rule'),
    path(r'rules/remove/<str:crypto>/<int:ruleset_id>/<int:rule_id>', RemoveRuleView.as_view(), name='remove_rule')
]
