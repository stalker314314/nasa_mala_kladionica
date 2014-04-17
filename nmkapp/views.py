# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response, get_object_or_404
from django.template.context import RequestContext, Context
from nmkapp.models import Round, UserRound, Shot, Match, Team, Player
from django.contrib.auth.decorators import login_required
from operator import itemgetter
from django.contrib.admin.views.decorators import staff_member_required
from django.db import transaction
from django.contrib import messages
from nmkapp.forms import RoundForm, MatchForm, ResultsForm, BettingForm
from django.http.response import HttpResponseRedirect, HttpResponseServerError
from django.contrib.auth.models import User
from nmkapp.logic import recalculate_round_points
from datetime import datetime
from django.db.models.aggregates import Min
from django.template import loader
from django.core.mail.message import EmailMessage

@login_required
@transaction.atomic
def home(request):
    active_rounds = Round.objects.filter(active=True).order_by("id")
    if len(active_rounds) == 0:
        messages.add_message(request, messages.INFO, u"Trenutno nema aktivnog kola za klađenje, pokušajte kasnije")
        return render_to_response("home.html", {"shots": []}, context_instance=RequestContext(request))

    bets = []
    for active_round in active_rounds:
        user_rounds = UserRound.objects.filter(user=request.user).filter(round=active_round)
        if len(user_rounds) != 1:
            messages.add_message(request, messages.INFO, u"Trenutno nema aktivnog kola za klađenje, pokušajte kasnije")
            return render_to_response("home.html", {"shots": []}, context_instance=RequestContext(request))
    
        user_round = user_rounds[0]
        shots = Shot.objects.filter(user_round=user_round).order_by("match__start_time")
        if len(shots) == 0:
            matches = Match.objects.filter(round=user_round.round).order_by("start_time")
            shots = []
            for match in matches:
                shot = Shot(user_round=user_round, match=match)
                shots.append(shot)

        betting_allowed = True
        for shot in shots:
            if shot.match.start_time < datetime.now():
                betting_allowed = False
                break
    
        if not user_round.shot_allowed:
            betting_allowed = False

        form = None
        if betting_allowed:
            if request.method == 'POST' and\
                    ('save_'+str(active_round.id) in request.POST or 'final_save_'+str(active_round.id) in request.POST):
                form = BettingForm(request.POST, shots=shots)
                if form.is_valid():
                    for user_round_match in form.cleaned_data:
                        user_round_id = int(user_round_match.split("_")[0])
                        match_id = int(user_round_match.split("_")[1])
                        shot = next(shot for shot in shots if shot.user_round.id==user_round_id and shot.match.id==match_id)
                        if shot != None:
                            shot.shot=form.cleaned_data[user_round_match]
                            shot.save()
                    if 'final_save_'+str(active_round.id) in request.POST:
                        user_round.shot_allowed = False
                        user_round.save()
                    messages.add_message(request, messages.INFO, u"Tipovanje uspešno sačuvano")
                    return HttpResponseRedirect('/')
            else:
                form = BettingForm(shots=shots)
    
        one_round_to_bet = {"form": form, "shots": shots, "round": active_round}
        bets.append(one_round_to_bet)
    return render_to_response("home.html", {"bets": bets}, context_instance=RequestContext(request))

@login_required
def results(request):
    return render_to_response("results.html", {}, context_instance=RequestContext(request))

@login_required
def results_league(request):
    groups = {}
    group_labels = Team.objects.values("group_label").order_by("group_label").distinct()
    for group_label in group_labels:
        matches = Match.objects.filter(round__group_type=Round.LEAGUE).filter(home_team__group_label=group_label["group_label"]).order_by("round")
        teams = Team.objects.filter(group_label = group_label["group_label"])
        league = []
        for team in teams:
            league.append([team.name, 0, 0, 0, 0, 0])
        for match in matches:
            if match.result == None: continue
            team_in_league = None
            for l in league:
                if l[0] == match.home_team.name:
                    team_in_league = l
            if team_in_league != None:
                team_in_league[1] += 1
                if match.result == 1:
                    team_in_league[2] += 1
                    team_in_league[5] += 3
                elif match.result == 0:
                    team_in_league[3] += 1
                    team_in_league[5] += 1
                else:
                    team_in_league[4] += 1
                    
            team_in_league = None
            for l in league:
                if l[0] == match.away_team.name:
                    team_in_league = l
            if team_in_league != None:
                team_in_league[1] += 1
                if match.result == 1:
                    team_in_league[4] += 1
                elif match.result == 0:
                    team_in_league[3] += 1
                    team_in_league[5] += 1
                else:
                    team_in_league[5] += 3
                    team_in_league[2] += 1
        league = sorted(league, key=itemgetter(5), reverse=True)
        groups[chr(group_label["group_label"] + ord('A'))] = {"league": league, "matches": matches}
    return render_to_response("results_league.html", {"groups": groups}, context_instance=RequestContext(request))

@login_required
def results_cup(request):
    rounds = []
    all_rounds = Round.objects.filter(group_type = Round.CUP).order_by("id")
    for my_round in all_rounds:
        matches = Match.objects.filter(round = my_round).order_by("start_time")
        one_round = [my_round, matches]
        rounds.append(one_round)
    return render_to_response("results_cup.html", { "rounds": rounds}, context_instance=RequestContext(request))

@login_required
def standings(request):
    standings = []
    rounds = list(Round.objects.order_by("id"))
    user_rounds = list(UserRound.objects.all())
    players = list(Player.objects.all())
    for player in players:
        round_standings = []
        for this_round in rounds:
            user_round = next((x.points for x in user_rounds if x.user==player.user and x.round==this_round), 0)
            round_standings.append(user_round)
        standing = [ player, round_standings, player.points ]
        standings.append(standing)
    standings = sorted(standings, key=itemgetter(2), reverse=True)
    return render_to_response("standings.html", { "rounds": rounds, "standings": standings}, context_instance=RequestContext(request))

@login_required
def round_standings(request, round_id):
    this_round = get_object_or_404(Round, pk=int(round_id))
    matches = list(Match.objects.filter(round=this_round).order_by("start_time"))
    round_standings = {}
    player_points = {}
    players = list(Player.objects.all())
    for player in players:
        user_rounds = UserRound.objects.filter(user=player.user).filter(round=this_round)
        if len(user_rounds) != 1:
            continue
        user_round = user_rounds[0]
        shots = list(Shot.objects.filter(user_round=user_round).order_by("match__start_time"))
        round_standings[user_round] = shots
        player_points[user_round] = user_round.points
    return render_to_response("roundstandings.html", {
                "matches": matches,
                "round_standings": round_standings,
                "player_points": player_points}, context_instance=RequestContext(request))

@login_required
def download(request):
    return render_to_response("download.html", {}, context_instance=RequestContext(request))

def proposition(request):
    return render_to_response("proposition.html", {}, context_instance=RequestContext(request))

@staff_member_required
def admin_rounds(request):
    rounds = Round.objects.order_by("id")
    message = ""
    set_active = request.GET.get('set_active', "0")
    try:
        set_active_id = int(set_active)
    except ValueError:
        #Try float.
        set_active_id = 0
    set_inactive = request.GET.get('set_inactive', "0")
    try:
        set_inactive_id = int(set_inactive)
    except ValueError:
        #Try float.
        set_inactive_id = 0
    if set_active_id != 0:
        should_be_active_round = get_object_or_404(Round, pk=int(set_active_id))
        should_be_active_round.active = True
        should_be_active_round.save()
        message = u"Kolo %s postavljeno kao aktivno" % should_be_active_round.name
        messages.add_message(request, messages.INFO, message)
        
        all_players = Player.objects.all()
        all_user_mail = [player.user.email for player in all_players if player.send_mail==True and player.user.email != ""]
        if len(all_user_mail) > 0:
            start_time = Match.objects.filter(round=should_be_active_round).aggregate(Min('start_time'))['start_time__min']
            template = loader.get_template("mail/round_active.html")
            message_text = template.render(Context({"round": should_be_active_round, "start_time": start_time }))
            msg = EmailMessage("[nmk] Novo aktivno kolo %s" % should_be_active_round.name, message_text, "nmk-no-reply@nmk.kokanovic.org", all_user_mail)
            msg.content_subtype = "html"
            msg.send(fail_silently = False)
    elif set_inactive_id != 0:
        should_be_inactive_round = get_object_or_404(Round, pk=int(set_inactive_id))
        should_be_inactive_round.active = False
        should_be_inactive_round.save()
        message = u"Kolo %s postavljeno kao neaktivno" % should_be_inactive_round.name
        messages.add_message(request, messages.INFO, message)

    return render_to_response("admin_rounds.html", {"rounds": rounds}, context_instance=RequestContext(request))

@staff_member_required
@transaction.atomic
def admin_rounds_edit(request):
    if request.method == 'POST':
        form = RoundForm(request.POST)
        if form.is_valid():
            new_round = form.save()
            users = User.objects.all()
            for user in users:
                user_round = UserRound(user=user, round=new_round, shot_allowed=True, points=0)
                user_round.save()
            messages.add_message(request, messages.INFO, u"Novo kolo %s uspešno kreirano" % new_round.name)
            return HttpResponseRedirect('/admin/rounds')
    else:
        form = RoundForm()

    return render_to_response("admin_rounds_edit.html", {"form": form,}, context_instance=RequestContext(request))

@staff_member_required
def admin_matches(request):
    matches = Match.objects.order_by("round__id", "start_time")
    return render_to_response("admin_matches.html", {"matches": matches}, context_instance=RequestContext(request))

@staff_member_required
@transaction.atomic
def admin_matches_edit(request):
    if request.method == 'POST':
        form = MatchForm(request.POST)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.INFO, u"Meč uspešno dodat")
            return HttpResponseRedirect('/admin/matches')
    else:
        form = MatchForm()

    return render_to_response("admin_matches_edit.html", {"form": form,}, context_instance=RequestContext(request))

@staff_member_required
def admin_results(request):
    current_rounds = Round.objects.filter(active=True)
    matches = []
    for current_round in current_rounds:
        one_round_matches = Match.objects.filter(round=current_round)
        matches.extend(one_round_matches)
    return render_to_response("admin_results.html", {"matches": matches}, context_instance=RequestContext(request))

@staff_member_required
@transaction.atomic
def admin_results_change(request, match_id):
    match = get_object_or_404(Match, pk=int(match_id))

    if request.method == 'POST':
        form = ResultsForm(request.POST, instance=match)
        if form.is_valid():
            match = form.save(commit=False)
            scores = match.score.split(":")
            score_home = int(scores[0])
            score_away = int(scores[1])
            if score_home > score_away:
                match.result = 1
            elif score_home == score_away:
                match.result = 0
            else:
                match.result = 2
            match.save()
            recalculate_round_points(match.round)
            messages.add_message(request, messages.INFO, u"Rezultat uspešno unesen")
            return HttpResponseRedirect('/admin/results')
    else:
        form = ResultsForm(instance=match)

    return render_to_response("admin_results_change.html", {"form": form, "match": match}, context_instance=RequestContext(request))