from django.conf.urls import url, include
from nmkapp import views
from django.contrib.auth.views import logout_then_login

urlpatterns = [
    url(r'^$', views.home),
    url(r'^register$', views.register),
    url(r'^register/success$', views.register_success),
    url(r'^activate$', views.activation),
    url(r'^forgotpassword', views.forgotpassword),
    url(r'^login/$', views.CustomLoginView.as_view(template_name='login.html', extra_context={'no_menu': True}),
        name='login'),
    url('', include('social_django.urls', namespace='social')),
    url(r'^requestdisplayname$', views.request_display_name, name='request_display_name'),
    url(r'^logout$', logout_then_login),
    url(r'^profile/reset$', views.reset_password),
    url(r'^profile/password$', views.CustomPasswordChangeView.as_view(
        template_name='password.html', success_url='/'), name='password_change'),
    url(r'^profile/create_password$', views.create_password, name='create_password'),
    url(r'^profile$', views.profile),
    url(r'^crew', views.crew),
    url(r'^standings$', views.standings),
    url(r'^roundstandings/(?P<round_id>\d+)$', views.round_standings),
    url(r'^groups/(?P<group_id>\d+)/leave', views.group_leave),
    url(r'^groups/(?P<group_id>\d+)/delete', views.group_delete),
    url(r'^proposition$', views.proposition),
    url(r'^about$', views.about),
    url(r'^privacy$', views.privacy),
    url(r'^terms$', views.terms),
    url(r'^paypal$', views.paypal),
    url(r'^landing$', views.landing),
    url(r'^admin/rounds$', views.admin_rounds),
    url(r'^admin/rounds/edit$', views.admin_rounds_edit),
    url(r'^admin/matches$', views.admin_matches),
    url(r'^admin/matches/edit$', views.admin_matches_edit),
    url(r'^admin/results$', views.admin_results),
    url(r'^admin/results/change/(?P<match_id>\d+)$', views.admin_results_change),
    url(r'^admin/points$', views.admin_points),
]
