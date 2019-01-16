from django.urls import path
from .views import *

app_name = 'crypto'


urlpatterns = [
    path(r'history/<str:crypto>/', get_crypto_history, name='history'),
    path(r'rulesets/<str:crypto>/', RulesetsView.as_view(), name='rulesets'),
    path(r'ruleset/add_or_edit/<str:crypto>/<int:ruleset_id>/', AddEditRulesetView.as_view(), name='add_edit_ruleset')
]
