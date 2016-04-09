from django.conf.urls import patterns, url
from nmkapp import views
from django.contrib.auth.views import logout_then_login, login, password_change

urlpatterns = patterns('',
    url(r'^$', views.home),
    url(r'^register$', views.register),
    url(r'^activate$', views.activation),
    url(r'^login/$', login, {'template_name': 'login.html'}),
    url(r'^logout$', logout_then_login),
    url(r'^profile$', views.profile),
    url(r'^password$', password_change, {"template_name": "password.html", "post_change_redirect": "/"}),
    url(r'^results$', views.results),
    url(r'^results/league$', views.results_league),
    url(r'^results/cup$', views.results_cup),
    url(r'^standings$', views.standings),
    url(r'^roundstandings/(?P<round_id>\d+)$', views.round_standings),
    url(r'^download$', views.download),
    url(r'^proposition$', views.proposition),
    url(r'^admin/rounds$', views.admin_rounds),
    url(r'^admin/rounds/edit$', views.admin_rounds_edit),
    url(r'^admin/matches$', views.admin_matches),
    url(r'^admin/matches/edit$', views.admin_matches_edit),
    url(r'^admin/results$', views.admin_results),
    url(r'^admin/results/change/(?P<match_id>\d+)$', views.admin_results_change),
)
