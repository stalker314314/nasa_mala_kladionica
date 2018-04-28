from django.conf.urls import url
from nmkapp import views
from django.contrib.auth.views import logout_then_login, login, password_change

urlpatterns = [
    url(r'^$', views.home),
    url(r'^register$', views.register),
    url(r'^activate$', views.activation),
    url(r'^forgotpassword', views.forgotpassword),
    url(r'^login/$', views.CustomLoginView.as_view(template_name='login.html', extra_context={'no_menu': True}),
        name='login'),
    url(r'^logout$', logout_then_login),
    url(r'^profile/reset$', views.reset_password),
    url(r'^profile/password$', password_change, {"template_name": "password.html", "post_change_redirect": "/"}),
    url(r'^profile$', views.profile),
    url(r'^results$', views.results),
    url(r'^results/league$', views.results_league),
    url(r'^results/cup$', views.results_cup),
    url(r'^standings$', views.standings),
    url(r'^roundstandings/(?P<round_id>\d+)$', views.round_standings),
    url(r'^groups/(?P<group_id>\d+)/leave', views.group_leave),
    url(r'^groups/(?P<group_id>\d+)/delete', views.group_delete),
    url(r'^download$', views.download),
    url(r'^proposition$', views.proposition),
    url(r'^paypal$', views.paypal),
    url(r'^admin/rounds$', views.admin_rounds),
    url(r'^admin/rounds/edit$', views.admin_rounds_edit),
    url(r'^admin/matches$', views.admin_matches),
    url(r'^admin/matches/edit$', views.admin_matches_edit),
    url(r'^admin/results$', views.admin_results),
    url(r'^admin/results/change/(?P<match_id>\d+)$', views.admin_results_change),
]
