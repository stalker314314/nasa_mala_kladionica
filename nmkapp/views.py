# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response, get_object_or_404
from django.template.context import RequestContext, Context
from nmkapp.models import Round, UserRound, Shot, Match, Team, Player, Group
from nmkapp.cache import StandingsCache, UserRoundShotCache
from django.contrib.auth.decorators import login_required
from operator import itemgetter
from django.contrib.admin.views.decorators import staff_member_required
from django.db import transaction
from django.contrib import messages
from nmkapp.forms import RoundForm, MatchForm, ResultsForm, BettingForm, PlayerForm
from nmkapp.forms import RegisterForm, ForgotPasswordForm, ResetPasswordForm, NewGroupForm, AddToGroupForm
from django.http.response import HttpResponseRedirect, HttpResponseServerError,\
    Http404
from django.contrib.auth.models import User
from nmkapp.logic import recalculate_round_points
from datetime import datetime
from django.db.models.aggregates import Min
from django.template import loader
from django.conf import settings
from django.core.mail.message import EmailMessage
import logging
import string
import random

logger = logging.getLogger(__name__)

def id_generator(size=16, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

@transaction.atomic
def register(request):
    logger.info("User is on register page")
    last_registration_time = datetime(2016, 6, 10, 20, 0)
    if datetime.now() >= last_registration_time:
        raise Http404()

    registered = False
    if request.method == 'POST':
        form = RegisterForm(request.POST, user={})
        if form.is_valid():
            cleaned_data = form.cleaned_data
            user = User.objects.create_user(username = cleaned_data['username'],
                                            email = cleaned_data['email'],
                                            password = cleaned_data['password'],
                                            first_name = cleaned_data['first_name'],
                                            last_name = cleaned_data['last_name'],
                                            is_active = False,
                                            last_login = datetime.now())
            user.player.activation_code = id_generator()
            user.player.save()

            template = loader.get_template("mail/registered.html")
            message_text = template.render(Context({"link": "http://nmk.kokanovic.org/activate?id=%s" % user.player.activation_code}))
            logger.info("Sending mail that user is registered to %s", user.email)
            msg = EmailMessage(u"[nmk] Registracija na NMK uspešna", message_text, "nmk-no-reply@nmk.kokanovic.org", to=[user.email,])
            msg.content_subtype = "html"
            msg.send(fail_silently = False)
            registered = True
    else:
        form = RegisterForm(user={})
    return render_to_response("register.html", {"form": form, 'registered': registered}, context_instance=RequestContext(request))

@transaction.atomic
def forgotpassword(request):
    logger.info("User is on forgot password page")
    reset = False
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST, rp={})
        if form.is_valid():
            cleaned_data = form.cleaned_data
            users = User.objects.filter(email=cleaned_data['email'])
            if len(users) > 0:
                user = users[0]
                user.player.reset_code = id_generator(size=32)
                user.player.save()

                template = loader.get_template("mail/resetpassword.html")
                message_text = template.render(Context({
                                                        "link": "http://nmk.kokanovic.org/profile/reset?id=%s" % user.player.reset_code,
                                                        "username": user.username}))
                logger.info("Sending mail to reset user's password to %s", user.email)
                msg = EmailMessage(u"[nmk] Zahtev za resetovanjem lozinke", message_text, "nmk-no-reply@nmk.kokanovic.org", to=[user.email,])
                msg.content_subtype = "html"
                msg.send(fail_silently = False)
                reset = True
    else:
        form = ForgotPasswordForm(rp={})
    return render_to_response("forgotpassword.html", {"form": form, 'reset': reset}, context_instance=RequestContext(request))

@transaction.atomic
def activation(request):
    logger.info("User is on activation page")
    activation_id = request.GET.get('id', '')
    success = False

    if activation_id != '':
        players = Player.objects.filter(activation_code = activation_id)
        if len(players) == 1:
            players[0].user.is_active = True
            players[0].user.save()
            success = True
    return render_to_response("activation.html", {"success": success}, context_instance=RequestContext(request))

@transaction.atomic
def reset_password(request):
    logger.info("User is on reset password page")
    reset_code = request.GET.get('id', '')
    nonvalid = True
    reset = False
    if reset_code != '':
        players = Player.objects.filter(reset_code = reset_code)
        if len(players) == 1:
            player = players[0]
            nonvalid = False
    if nonvalid:
        return render_to_response("resetpassword.html", {"nonvalid": nonvalid}, context_instance=RequestContext(request))

    if request.method == 'POST':
        form = ResetPasswordForm(request.POST, passwords={})
        if form.is_valid():
            cleaned_data = form.cleaned_data
            player.user.set_password(cleaned_data['password'])
            player.user.save()
            reset = True
    else:
        form = ResetPasswordForm(passwords={})
    return render_to_response("resetpassword.html",
                              {"form": form, "id": reset_code, "nonvalid": nonvalid, "reset": reset, "username": player.user.username},
                              context_instance=RequestContext(request))

@login_required
@transaction.atomic
def home(request):
    logger.info("User %s is on betting page", request.user)
    active_rounds = Round.objects.filter(active=True).order_by("id")
    if len(active_rounds) == 0:
        messages.add_message(request, messages.INFO, u"Trenutno nema aktivnog kola za klađenje, pokušaj kasnije")
        return render_to_response("home.html", {"shots": []}, context_instance=RequestContext(request))

    bets = []
    for active_round in active_rounds:
        user_rounds = UserRound.objects.select_related('round').filter(user=request.user).filter(round=active_round)
        if len(user_rounds) != 1:
            messages.add_message(request, messages.INFO, u"Trenutno nema aktivnog kola za klađenje, pokušaj kasnije")
            return render_to_response("home.html", {"shots": []}, context_instance=RequestContext(request))
    
        user_round = user_rounds[0]
        shots = Shot.objects.select_related('match', 'match__home_team', 'match__away_team', 'user_round').filter(user_round=user_round).order_by("match__start_time")
        if len(shots) == 0:
            matches = Match.objects.select_related('home_team', 'away_team').filter(round=user_round.round).order_by("start_time")
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
                logger.info("User %s posted betting", request.user)
                form = BettingForm(request.POST, shots=shots)
                if form.is_valid():
                    logger.info("User %s posted valid form %s", request.user, form.cleaned_data)
                    for user_round_match in form.cleaned_data:
                        user_round_id = int(user_round_match.split("_")[0])
                        match_id = int(user_round_match.split("_")[1])
                        shot = next(shot for shot in shots if shot.user_round.id==user_round_id and shot.match.id==match_id)
                        if shot != None:
                            shot.shot=form.cleaned_data[user_round_match]
                            shot.save()
                    if 'final_save_'+str(active_round.id) in request.POST:
                        logger.info("User %s posted final save", request.user)
                        user_round.shot_allowed = False
                        user_round.save()
                    UserRoundShotCache(user_round).clear()
                    messages.add_message(request, messages.INFO, u"Tipovanje uspešno sačuvano")
                    return HttpResponseRedirect('/')
            else:
                form = BettingForm(shots=shots)

        time_left = format_time_left(shots)
        one_round_to_bet = {"form": form, "shots": shots, "round": active_round, "time_left": time_left}
        bets.append(one_round_to_bet)
    return render_to_response("home.html", {"bets": bets}, context_instance=RequestContext(request))

def format_time_left(shots):
    if len(shots) > 0:
        seconds_left = (shots[0].match.start_time - datetime.now()).total_seconds()
        if seconds_left > 60*60*24:
            days = int(seconds_left/(60*60*24))
            return "%dd %dh" % (days, int((seconds_left - (days * 60 * 60 * 24))/(60 * 60)))
        elif seconds_left > 60*60:
            hours = int(seconds_left/(60*60))
            return "%dh %dmin" % (hours, int((seconds_left - hours *60 * 60)/60))
        elif seconds_left > 60:
            minutes = int(seconds_left/60)
            print(seconds_left, minutes)
            return "%dmin %dsec" % (minutes, int(seconds_left - minutes * 60))
        elif seconds_left > 0:
            return "%dsec" % seconds_left
        else:
            return "prvi meč već počeo"
    else:
        return "N/A"

@login_required
@transaction.atomic
def profile(request):
    if request.method == 'POST' and 'profile_change' in request.POST:
        form = PlayerForm(request.POST, instance=request.user.player)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.INFO, u"Podešavanja uspešno sačuvana")
    else:
        form = PlayerForm(instance=request.user.player)

    if request.method == 'POST' and 'new_group' in request.POST:
        form_new_group = NewGroupForm(request.POST, group={})
        if form_new_group.is_valid():
            cleaned_data = form_new_group.cleaned_data
            new_group = Group(name = cleaned_data['name'], group_key = id_generator(size=8, chars=string.digits), owner = request.user.player)
            new_group.save()
            new_group.players.add(request.user.player)
            new_group.save()
            messages.add_message(request, messages.INFO,
                                 u"Uspešno si napravio novu ekipu. Sad pošalji chat-om/mail-om/SMS-om prijateljima šifru-pozivnicu '%s' \
                                 da bi mogli i oni da uđu u tvoju ekipu" % new_group.group_key)
    else:
        form_new_group = NewGroupForm(group={})

    if request.method == 'POST' and 'add_to_group' in request.POST:
        form_add_group = AddToGroupForm(request.user.player, request.POST, group_key={})
        if form_add_group.is_valid():
            cleaned_data = form_add_group.cleaned_data
            groups = Group.objects.filter(group_key = cleaned_data['key'])
            group = groups[0]
            group.players.add(request.user.player)
            group.save()
            messages.add_message(request, messages.INFO, u"Uspešno si se dodao u ekipu")
    else:
        form_add_group = AddToGroupForm(request.user.player, group_key={})

    groups = Group.objects.filter(player__in=[request.user.player])
    return render_to_response(
                              "profile.html",
                              {"form": form, "form_new_group": form_new_group, "form_add_group": form_add_group,
                               "groups": groups, "current_user": request.user.player},
                              context_instance=RequestContext(request))

@login_required
def results(request):
    return render_to_response("results.html", {}, context_instance=RequestContext(request))

@login_required
def results_league(request):
    groups = []
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
        groups.append({"league": league, "matches": matches, "label": chr(group_label["group_label"] + ord('A'))}) 
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
    selected_group = request.GET.get('group', '')
    all_groups = Group.objects.filter(player__in=[request.user.player])
    group = Group.objects.filter(player__in=[request.user.player]).filter(name=selected_group)
    if len(group) != 1:
        selected_group = ''
        group = None
    else:
        group = group[0]
    rounds = Round.objects.order_by("id")
    
    standings = StandingsCache(group).get(rounds)

    return render_to_response("standings.html", {
            "rounds": rounds,
            "standings": standings,
            "groups": all_groups,
            "selected_group": selected_group}, context_instance=RequestContext(request))

@login_required
@transaction.atomic
def group_leave(request, group_id):
    group = get_object_or_404(Group, pk=int(group_id))
    # Check if user is in group at all
    if len(Group.objects.filter(pk = int(group_id)).filter(player__in=[request.user.player])) == 0:
        raise Http404()
    # Check if user is owner of the group
    error = None
    if request.user.player == group.owner:
        error = "Ne možeš da izađeš iz ekipe koju si ti napravio, možeš samo da je izbrišeš skroz."

    if not error and request.method == 'POST':
        if '0' in request.POST:
            return HttpResponseRedirect('/profile')
        elif '1' in request.POST:
            group.players.remove(request.user.player)
            messages.add_message(request, messages.INFO, u"Izašao si iz ekipe '%s'" % group.name)
            return HttpResponseRedirect('/profile')
    return render_to_response("group_leave.html", {"error": error, "group": group}, context_instance=RequestContext(request))

@login_required
@transaction.atomic
def group_delete(request, group_id):
    group = get_object_or_404(Group, pk=int(group_id))
    # Check if user is in group at all
    if len(Group.objects.filter(pk = int(group_id)).filter(player__in=[request.user.player])) == 0:
        raise Http404()
    # Check if user is owner of the group
    error = None
    if request.user.player != group.owner:
        error = "Ne možeš da izbrišeš ekipu koju nisi ti napravio, možeš samo da izađeš iz nje."

    if not error and request.method == 'POST':
        if '0' in request.POST:
            return HttpResponseRedirect('/profile')
        elif '1' in request.POST:
            group.players.clear()
            group.delete()
            messages.add_message(request, messages.INFO, u"Ekipa '%s' izbrisana" % group.name)
            return HttpResponseRedirect('/profile')
    return render_to_response("group_delete.html", {"error": error, "group": group}, context_instance=RequestContext(request))

@login_required
def round_standings(request, round_id):
    this_round = get_object_or_404(Round, pk=int(round_id))
    matches = Match.objects.select_related('round', 'home_team', 'away_team').filter(round=this_round).order_by("start_time", "id")

    selected_group = request.GET.get('group', '')
    all_groups = Group.objects.filter(player__in=[request.user.player])
    group = Group.objects.filter(player__in=[request.user.player]).filter(name=selected_group)
    if len(group) != 1:
        selected_group = ''
        group = None
    else:
        group = group[0]
        
    can_see_standings = False
    is_any_match_started = False
    for match in matches:
        if match.start_time < datetime.now():
            is_any_match_started = True
            break
    if is_any_match_started:
        can_see_standings = True
    else:
        logged_user_rounds = UserRound.objects.filter(user=request.user, round=this_round)
        if len(logged_user_rounds)==1 and logged_user_rounds[0].shot_allowed==False:
            can_see_standings = True

    round_standings = []
    
    position = 1
    previous_points = None
    position_increment = 1
    
    if can_see_standings:
        user_rounds = UserRound.objects.select_related('user', 'user__player').filter(round=this_round)
        if group is not None:
             user_rounds = user_rounds.filter(user__player__groups__in=[group])
        user_rounds = user_rounds.order_by("-points", "user__first_name", "user__last_name")
        
        for user_round in user_rounds:
            shots = UserRoundShotCache(user_round).get();
            
            if previous_points != None:
                if previous_points != user_round.points:
                    position += position_increment
                    position_increment = 1
                else:
                    position_increment += 1
            previous_points = user_round.points
            round_standings.append({"user_round": user_round, "shots": shots, "position": position})

    return render_to_response("roundstandings.html", {
                "can_see_standings": can_see_standings,
                "round": round,
                "matches": matches,
                "round_standings": round_standings,
                "round": this_round,
                "groups": all_groups,
                "selected_group": selected_group}, context_instance=RequestContext(request))

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
        
        if settings.SEND_MAIL:
            all_players = Player.objects.all()
            all_user_mail = [player.user.email for player in all_players if player.send_mail==True and player.user.email != ""]
            start_time = Match.objects.filter(round=should_be_active_round).aggregate(Min('start_time'))['start_time__min']
            template = loader.get_template("mail/round_active.html")
            message_text = template.render(Context({"round": should_be_active_round, "start_time": start_time }))
            logger.info("Sending mail that round %s is active to %s", should_be_active_round.name, all_user_mail)
            for user_mail in all_user_mail:
                msg = EmailMessage(u"[nmk] Novo aktivno kolo %s" % should_be_active_round.name, message_text, "nmk-no-reply@nmk.kokanovic.org", to=[user_mail,])
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
            groups = Group.objects.all()
            for group in groups:
                StandingsCache(group).clear()
            StandingsCache().clear()
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
    matches = Match.objects.all()
#     for current_round in current_rounds:
#         one_round_matches = Match.objects.filter(round=current_round)
#         matches.extend(one_round_matches)
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
            logger.info("User %s set result for match %s", request.user, match)
            recalculate_round_points(match.round)
            messages.add_message(request, messages.INFO, u"Rezultat uspešno unesen")
            
            # invalidate cache of shots for all user in this round
            user_rounds = UserRound.objects.filter(round=match.round)
            for user_round in user_rounds:
                UserRoundShotCache(user_round).clear()
            groups = Group.objects.all()
            for group in groups:
                StandingsCache(group).clear()
            StandingsCache().clear()

            # send mail if this is the last match from round
            if settings.SEND_MAIL:
                count_matches_without_result = Match.objects.all().filter(round=match.round).filter(result__isnull=True).count()
                if count_matches_without_result == 0:
                    all_players = Player.objects.all()
                    all_user_mail = [player.user.email for player in all_players if player.send_mail==True and player.user.email != ""]
                    logger.info("Sending mail that round %s have all results to %s", match.round, all_user_mail)
                    template = loader.get_template("mail/result_added.html")
                    message_text = template.render(Context({"round": match.round}))
                    for user_mail in all_user_mail:
                        msg = EmailMessage(u"[nmk] Uneti svi rezultati mečeva iz kola \"%s\"" % (match.round.name), message_text, "nmk-no-reply@nmk.kokanovic.org", to=[user_mail,])
                        msg.content_subtype = "html"
                        msg.send(fail_silently = False)
                
            return HttpResponseRedirect('/admin/results')
    else:
        form = ResultsForm(instance=match)

    return render_to_response("admin_results_change.html", {"form": form, "match": match}, context_instance=RequestContext(request))